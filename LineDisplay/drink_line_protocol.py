from .line_protocol import LineDisplayProtocolBase
from .line_protocol import ItemData
from .widgets import ScrollingUpdate
from .line_protocol import HEADER_OPT, NULL_OPT, ITEM_OPT
from Printer import Printer
import lib


class DrinkLineProtocol(LineDisplayProtocolBase):
    
    def __init__(self, include=None, exclude=None):
        super().__init__("Display1", _print=False)
        self.printer = Printer()
        if include is None:
            include = list()
        if exclude is None:
            exclude = list()
        self.include = include
        self.exclude = exclude
    
    # Some drinks don't need to show up. but they also need to be marked complete
    def set_excluded_item_status(self, item):
        self.create_task(self.server_message(
                "set_item_status",
                data=(
                    (item.dim3,),
                    lib.TICKET_COMPLETE)))

    def filter(self, ticket, ticket_no, index, subindex):
        if ticket.parameters.get("register", False):
            if (any(exclude in ticket.name for exclude in self.exclude)
                    and ticket.name not in self.include):
                if ticket.parameters.get("status") != lib.TICKET_COMPLETE: 
                    self.set_excluded_item_status(ItemData(ticket, ticket_no, index, subindex))
                ticket = lib.NULL_TICKET_ITEM
        else:
            ticket = lib.NULL_TICKET_ITEM
        return ItemData(ticket, ticket_no, index, subindex)

    def receipt(self, ticket, status):
        if not ticket or all(item.parameters.get("status") == lib.TICKET_COMPLETE for item in ticket if item):
            return []

        header = "{:03d}: {}" if ticket.name else "{:03d}"
        header = (header.format(ticket.ticket_no, ticket.name)\
                if ticket.name else header.format(ticket.ticket_no))
        header = header, HEADER_OPT
        if status == lib.PRINT_NEW:
            status = "NEW TICKET", HEADER_OPT
        elif status == lib.PRINT_MOD:
            status = "MODIFIED TICKET", HEADER_OPT
        elif status == lib.PRINT_NUL:
            status = "CANCELED TICKET", HEADER_OPT

        lines = [header, status]
        if ticket.deliver:
            lines.append(("DELIVER", HEADER_OPT))
        for item in ticket:
            if not item.name:
                continue
            lines.append((item.name, NULL_OPT))
            lines.append((("\n".join(f"  +  {option}"), NULL_OPT) for option in item.selected_options))
        return lines
            