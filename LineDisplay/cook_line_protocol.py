from .line_protocol import LineDisplayProtocolBase
from .line_protocol import ItemData, TicketData
from .line_protocol import ITEM_OPT, NULL_OPT, HEADER_OPT
from .widgets import ScrollingUpdate
from Printer import Printer
import threading
import lib
import asyncio
import queue
import websockets




class CookLineProtocol(LineDisplayProtocolBase):

    def __init__(self):
        super().__init__("Display0")

    def filter(self, ticket, ticket_no, index, subindex):
        ticket = (lib.NULL_TICKET_ITEM
                if ticket.parameters.get("register", False)
                else ticket)
        return ItemData(ticket, ticket_no, index, subindex)
    
    def receipt(self, ticket, status):
        if status == lib.PRINT_NEW:
            status = "NEW TICKET", HEADER_OPT
        elif status == lib.PRINT_MOD:
            status = "MODIFIED TICKET", HEADER_OPT
        elif status == lib.PRINT_NUL:
            status = "CANCELED TICKET", HEADER_OPT
        lines = list()  # generally an empty list instantiated with []. list() is usually only used to cast a type to list (e.g. list(some_tuple))
        # ticket.name -> name of customer
        # ticket.item.name -> name of menu item
        if ticket.name:
            header =  "{:03d}".format(
                        ticket.ticket_no) + f": {ticket.name}", HEADER_OPT
        else:
            header = "{:03d}".format(ticket.ticket_no), HEADER_OPT
        if not ticket.item.parameters.get("register"): 
            lines.append((ticket.item.name, ITEM_OPT))
            if ticket.item.parameters.get("comments", ""):
                lines.append(("  " + f"'{ticket.item.parameters.get('comments')}'", NULL_OPT))
            lines.extend(("  + " + option, NULL_OPT) for option in ticket.item.selected_options)
        
        if not ticket.addon1.parameters.get("register"):
            lines.append(("  " + ticket.addon1.name, ITEM_OPT))
            if ticket.addon1.parameters.get("comments", ""):
                lines.append(("    " + f"'{ticket.addon1.parameters.get('comments')}", NULL_OPT))            
            lines.extend(("    + " + option, NULL_OPT) for option in ticket.addon1.selected_options)
    
        if not ticket.addon2.parameters.get("register"):
            lines.append(("  " + ticket.addon2.name, ITEM_OPT))
            if ticket.addon2.parameters.get("comments", ""):
                lines.append("    " + (f"'{ticket.addon2.parameters.get('comments')}'", NULL_OPT))
            lines.extend(("    + " + option, NULL_OPT) for option in ticket.addon2.selected_options)
        if lines:
            lines.insert(0, status)
            lines.insert(0, header)
        return lines

