from Printer import Printer
import lib
import logging
import json
import websockets
import operator
import asyncio

NUM_TICKETS = 5
NULL_OPT = {}
HEADER_OPT = {
        "size":bytes("L", "utf-8"),
        "justify": bytes("C", "utf-8")}

ITEM_OPT = {
        "size": bytes("M", "utf-8")}

class OrderIndex(tuple, metaclass=lib.TicketType):
    """OrderIndex(ticket, ticket_no, nth_ticket)"""
    def __new__(cls, ticket, ticket_no, nth_ticket):
        item = ticket[:6]
        addon1 = lib.Ticket(ticket[6][:4], ticket[6][4], ticket[6][5])
        addon2 = lib.Ticket(ticket[7][:4], ticket[7][4], ticket[7][5])
        return super().__new__(cls, (*item, addon1, addon2, (ticket_no, nth_ticket)))
    
    def is_complete(self):
        return all(value == lib.TICKET_COMPLETE for value in self.status)
    
    def is_working(self):
        return all(value == lib.TICKET_WORKING for value in self.status)
    
    def is_queued(self):
        return all(value == lib.TICKET_QUEUED for value in self.status)

    def ticket_receipt(self, status, n_ticket):
        if status == lib.PRINT_NEW:
            status = "NEW TICKET", HEADER_OPT
        elif status == lib.PRINT_MOD:
            status = "MODIFIED TICKET", HEADER_OPT
        elif status == lib.PRINT_NUL:
            status = "CANCELED TICKET", HEADER_OPT
        lines = list()      
        header =  "{:03d} ({}/{})".format(
                    self.ticket_no, self.index[1] + 1, n_ticket), HEADER_OPT

        if not self.parameters.get("register"): # pylint: disable=E1101
            lines.append((self.name, ITEM_OPT)) # pylint: disable=E1101
            lines.extend(("  + " + option, NULL_OPT) for option in self.selected_options) # pylint: disable=E1101
        
        if not self.addon1.parameters.get("register"):
            lines.append(("  " + self.addon1.name, ITEM_OPT))
            lines.extend(("    + " + option, NULL_OPT) for option in self.addon1.selected_options)
        
        if not self.addon2.parameters.get("register"):
            lines.append(("  " + self.addon2.name, ITEM_OPT))
            lines.extend(("    + " + option, NULL_OPT) for option in self.addon2.selected_options)
        
        if lines:
            lines.insert(0, status)
            lines.insert(0, header)
        return lines

    @property
    def status(self):
        return (self.parameters.get("status"),  # pylint: disable=E1101
                self.addon1.parameters.get("status"),
                self.addon2.parameters.get("status"))
    
    @status.setter
    def status(self, value):
        self.parameters["status"] = lib.TICKET_WORKING # pylint: disable=E1101
        self.addon1.parameters["status"] = lib.TICKET_WORKING
        self.addon2.parameters["status"] = lib.TICKET_WORKING
        
    @property
    def ticket_no(self):
        return self.index[0]

    def get_lines(self):
        ...

    get = operator.itemgetter
    addon1 = property(get(6))
    addon2 = property(get(7))
    index = property(get(8))


class DisplayProtocol(lib.DisplayInterface):
    
    def __init__(self):
        super().__init__()
        self.ticket_printer = Printer("/dev/null")
        self.ticket_generator = None
        self.network = False
        self.connected = False
        self.test_network_connection()
        self.connect()
        self.print_tickets()
        self.show_num_tickets = NUM_TICKETS


    def tickets(self):
        if self.order_queue is None:
            return []        
        return [ticket for ticket in self.order_queue if not ticket.is_complete()]
        
    def loads(self, string):
        result = json.loads(string)
        self.ticket_no = result["ticket_no"]
        self.requests = result["requests"]
        self.connected_clients = result["connected_clients"]
        self.shutdown_now = result["shutdown_now"]

        self.order_queue = [
            OrderIndex(ticket, int(ticket_no), i)
            for ticket_no in result["order_queue"]
                for i, ticket in enumerate(result["order_queue"][ticket_no]["items"])]

        self.ticket_generator = ((ticket, 
                result["order_queue"][str(ticket.ticket_no)]["print"],
                len(result["order_queue"][str(ticket.ticket_no)]["items"]))
                for ticket in self.order_queue
                    if result["order_queue"][str(ticket.ticket_no)]["print"])

    def set_ticket_status(self, index, value):
        """set status of one ticket status to value"""
        data = index[0], index[1], value
        return self.loop.create_task(
            self.server_message("set_ticket_status", data))
    
    def set_order_status(self, ticket_no, value):
        """set status of entire order to value"""
        data = ticket_no, value
        return self.loop.create_task(self.server_message("set_order_status", data))
    
    def print_tickets(self):      
        
        async def not_none():
            while True:
                if self.ticket_generator is not None:
                    return
                await asyncio.sleep(1/30)

        async def _print_tickets():
            while True:
                for ticket in self.ticket_generator:
                    ticket, status, cnt = ticket
                    line_opt = ticket.ticket_receipt(status, cnt)
                    for line, opt in line_opt:
                        self.ticket_printer.writeline(line, **opt)
                    # make sure everything is above cutoff line
                    self.ticket_printer.writeline("\n\n\n", **NULL_OPT)
                    await self.server_message("set_ticket_printed", ticket)

                await asyncio.sleep(1/30)

        def print_tickets(task):
            self.loop.create_task(_print_tickets())

        # wait for server update
        task = self.loop.create_task(not_none())
        
        # start print_ticket loop
        task.add_done_callback(print_tickets)
        
