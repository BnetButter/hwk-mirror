from .metaclass import *
from .data import *
from .tkwidgets import *
from .stream import *
from .tkinterface import *
from .interface import *

# As long as I've been programming Python, I don't think I've ever needed to implement new(). In this case you should do this.
class OrderTicket(Ticket):
    """Base class for a complete Order ticket."""
    def __init__(self, item, addon1, addon2):
        self.item = item
        self.addon1 = addon1
        self.addon2 = addon2


NULL_MENU_ITEM = MenuItem("", "", 0, {}, "", 0)
NULL_TICKET_ITEM = Ticket(("", "", 0, {}, "", 0))
NULL_ORDER_ITEM = OrderTicket(NULL_TICKET_ITEM, NULL_TICKET_ITEM, NULL_TICKET_ITEM)
NULL_FUNC = lambda *args, **kwargs: ...
CONST_PAYMENT_TYPES = "Cash", "Check", "Invoice"


