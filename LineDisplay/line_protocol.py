from .widgets import ScrollingUpdate
from Printer import Printer
import lib
import operator
import collections
import abc
import threading
import queue
import asyncio


class Dim3(tuple):

    def __new__(cls, ticket_no, index, subindex):
        return super().__new__(cls, (ticket_no, index, subindex))
    @classmethod
    def convert_to(cls, z, y, x):
        return cls(z, y, x)

    subindex = property(operator.itemgetter(2))
    index = property(operator.itemgetter(1))
    ticket_no = property(operator.itemgetter(0))


class ItemData(tuple, metaclass=lib.TicketType):

    def __new__(cls, item, ticket_no, index, subindex):
        return tuple.__new__(cls, (*item, Dim3(ticket_no, index, subindex)))
    
    def __bool__(self):
        return bool(self.name)
    
    dim3 = property(operator.itemgetter(-1))

# can't use TicketType here since indices change
class TicketData:

    def __init__(self, ticket, ticket_no, index, name, deliver):
        self.item = lib.AsyncTk().forward("filter", ticket, ticket_no, index, 0)
        self.addon1 = lib.AsyncTk().forward("filter", ticket.addon1, ticket_no, index, 1)
        self.addon2 = lib.AsyncTk().forward("filter", ticket.addon2, ticket_no, index, 2)
        self.ticket_no = ticket_no
        self.index = index
        self.name = name
        self.deliver = deliver

    @classmethod
    def buffer(cls):
        return cls(lib.NULL_ORDER_ITEM, 0,0,0,0)

    def __bool__(self):
        return bool(self.item or self.addon1 or self.addon2)

    def completed(self):
        return tuple(item for item in self if item.parameters.get("status") == lib.TICKET_COMPLETE and item.name)

    def not_completed(self):
        return tuple(item for item in self if item.parameters.get("status") != lib.TICKET_COMPLETE and item.name)
    
    def all(self):
        return tuple(item for item in self if item)

    def __iter__(self):
        self.i = 0
        return self
    
    def __next__(self):
        if self.i == 0:
            result = self.item
        elif self.i == 1:
            result = self.addon1
        elif self.i == 2:
            result = self.addon2
        else:
            self.i = 0
            raise StopIteration
        self.i += 1
        return result
    



class LineDisplayProtocolBase(lib.ClientInterface, metaclass=abc.ABCMeta):

    def __init__(self, client_id, _class=TicketData, _print=True):
        super().__init__(client_id)
        self.connect()
        self.test_network_connection()
        self.data = list()
        assert issubclass(_class, TicketData)
        self.ticket_type = _class
        self.printer = Printer()
        self.print = _print
        self.start_printer()

    def set_print(self, value):
        self.print = bool(value)
    
    def tickets(self):
        return tuple(self.data)\
             + tuple(
                TicketData.buffer()
                for _ in range(ScrollingUpdate().show))

    def loads(self, string):
        result = super().loads(string)
        self.data = list()
        for ticket_no in self.order_queue:
            order_dct = self.order_queue[ticket_no]
            for index, ticket in enumerate(order_dct["items"]):
                ticket = order_dct["items"][index] = lib.Ticket.convert_to(*ticket)    
                result = self.ticket_type(
                        ticket,
                        int(ticket_no),
                        index,
                        order_dct["name"],
                        order_dct["deliver"])
                if result:
                    self.data.append(result)
        return result

    def on_enter(self, task):
        if task.result():
            return
        else:
            ScrollingUpdate().advance()

    def set_item_status(self, items, value):
        task = self.create_task(self.server_message(
                "set_item_status",
                data=(
                    tuple(item.dim3 for item in items if item),
                    value)))
        task.add_done_callback(self.on_enter)
        return task
    
    @abc.abstractmethod
    def filter(self) -> TicketData:
        """must return TicketData instance"""

    @abc.abstractmethod
    def receipt(self, ticket, print_status) -> [("", {}), ...]:
        """must return a list of (str, mapping)"""


    def start_printer(self):
        async def printer():
            while True:
                for ticket in self.data:
                    print_status = self.order_queue[str(ticket.ticket_no)]["print"]
                    if all(item.parameters.get("print", 1) for item in ticket if item):
                        if self.print:
                            lines = self.receipt(ticket, print_status)
                            if lib.DEBUG:
                                print("\n".join(line[0] for line in lines))
                            for line in lines:
                                self.printer.writeline(line[0], **line[1])
                            # give enough room to tear it out
                            self.printer.writeline("\n\n\n")
                            dim3s = tuple(item.dim3 for item in ticket if item)
                        # must be sent to the server (instead of keeping it in a local set)
                        # to prevent printing old tickets.
                        await self.server_message("set_item_printed", (dim3s, False))
                await asyncio.sleep(1/30)
        self.create_task(printer())


NULL_OPT = {}
HEADER_OPT = {
        "size":bytes("L", "utf-8"),
        "justify": bytes("C", "utf-8")}

ITEM_OPT = {
        "size": bytes("M", "utf-8")}