from .metaclass import *
from .data import *
from .tkwidgets import *
from .stream import *
from .tkinterface import *
from .interface import *

class OrderTicket(Ticket):
    """Base class for a complete Order ticket."""
    def __new__(cls, item, addon1, addon2):
        # embedded item
        return tuple.__new__(cls, (*item, addon1, addon2))


NULL_MENU_ITEM = MenuItem("", "", 0, {}, "", 0)
NULL_TICKET_ITEM = Ticket(("", "", 0, {}, "", 0))
NULL_ORDER_ITEM = OrderTicket(NULL_TICKET_ITEM, NULL_TICKET_ITEM, NULL_TICKET_ITEM)
NULL_FUNC = lambda *args, **kwargs: ...
CONST_PAYMENT_TYPES = "Cash", "Check", "Invoice"


