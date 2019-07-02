from .metaclass import *
from .data import *
from .tkwidgets import *
from .stream import *
from .tkinterface import *
from .interface import *

NULL_MENU_ITEM = MenuItem("", "", 0, {}, "", 0)
NULL_TICKET_ITEM = Ticket(("", "", 0, {}, "", 0))
NULL_FUNC = lambda *args, **kwargs: ...
CONST_PAYMENT_TYPES = "Cash", "Check", "Invoice"