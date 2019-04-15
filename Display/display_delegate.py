import lib
import logging
import json
import websockets
import operator
import asyncio


NUM_TICKETS = 5

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

    get = operator.itemgetter
    addon1 = property(get(6))
    addon2 = property(get(7))
    index = property(get(8))

class DisplayProtocol(lib.DisplayInterface):
    
    def __init__(self):
        super().__init__()
        self.network = False
        self.connected = False
        self.test_network_connection()
        self.connect()
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
    
    def set_ticket_status(self, index, value):
        """set status of one ticket status to value"""
        data = index[0], index[1], value
        return self.loop.create_task(
            self.server_message("set_ticket_status", data))
    
    def set_order_status(self, ticket_no, value):
        """set status of entire order to value"""
        data = ticket_no, value
        return self.loop.create_task(self.server_message("set_order_status", data))
    
