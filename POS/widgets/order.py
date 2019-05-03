from operator import itemgetter
from lib import MenuItem
from lib import MenuType
from lib import OrderInterface
from lib import SYS_STDOUT
from lib import log_info
from lib import Ticket
import logging

logger = logging.getLogger()

def new(cls, menu_item, addon1, addon2, selected_options=None):
    
    param1 = {"register": menu_item.category in cls.register, "status":None}
    param2 = {"register": addon1.category in cls.register, "status": None}
    param3 = {"register": addon2.category in cls.register, "status": None}

    addon1 = Ticket(addon1, parameters=param2)
    addon2 = Ticket(addon2, parameters=param3)    
    if selected_options is None:
        cls.data.append(tuple.__new__(cls, (*menu_item, list(), param1, addon1, addon2)))
    else:
        assert all(option in menu_item[3] for option in selected_options)
        cls.data.append(tuple.__new__(cls, (*menu_item,
            selected_options,
            param1,
            addon1,
            addon2)))

    logger.debug(f"added ticket: {menu_item.name, addon1.name, addon2.name}")

@property
def total(self):
    total = self.price
    for option in self.selected_options:
        total += self.options[option]
    
    cls = type(self)
    if self.category in cls.two_sides \
            or self.category in cls.no_addons:
        return total
    if self.category not in cls.include_drinks:        
        for addon in (self.addon1, self.addon2):
            if addon.category == "Drinks":
                total += addon.total
    if self.category not in cls.include_sides:
        for addon in (self.addon1, self.addon2):
            if addon.category == "Sides":
                total += addon.total
    return total

parameters = property(itemgetter(5))
addon1 = property(itemgetter(6))
addon2 = property(itemgetter(7))

def __str__(self):
    lines = list()
    lines.append(self.name)
    lines.extend([f"        + {option}" for option in self.selected_options])
    if self.addon1.name:
        lines.append("    " + self.addon1.name)
        lines.extend([f"        + {option}" for option in self.addon1.selected_options])
    if self.addon2.name:
        lines.append("    " + self.addon2.name)
        lines.extend([f"        + {option}" for option in self.addon2.selected_options])
    return "\n".join(lines)

receipt_printer_style = {
    "ticket_no": {
        "bold":bytes(1),
        "justify":bytes('C', "utf-8"),
        "size": bytes('L', "utf-8"),
    },
    "item": {
        "size": bytes('M', "utf-8"),
        "underline":bytes(1),
    },
    "total": {
        "justify":bytes('C', "utf-8"),
        "size": bytes('L', "utf-8"),
    },
}

MAX_WIDTH = 32

def line_fmt(name, price):
    price = "$ {:.2f}".format(price / 100)
    n_space = MAX_WIDTH - len(name) - len(price)
    if n_space < 0:
        ...
    return name + (n_space * " ") + price

def receipt(self) -> str:
    cls = type(self)
    lines = list()

    lines.append((line_fmt(self.name, self.price), receipt_printer_style["item"]))
    lines.extend((f"    + {option}", {}) for option in self.selected_options)
    
    addon1 = list(self.addon1) # make mutable
    addon2 = list(self.addon2)

    
    if self.category in cls.two_sides       \
            or self.category in cls.no_addons:
        addon1[2] = addon2[2] = 0 # set multiplier

    if self.category in cls.include_sides:
        for addon in (addon1, addon2):
            if addon[0] == "Sides":
                addon[2] = 0 
    
    if self.category in cls.include_drinks:
        for addon in (addon1, addon2):
            if addon[0] == "Drinks":
                addon[2] = 0
    
    
    # don't want to multiply price by itself so 
    # convert to bool.
    if self.addon1.name:
        lines.append((line_fmt("  " + self.addon1.name, 
                self.addon1.total * bool(addon1[2])), receipt_printer_style["item"]))
        lines.extend((f"    + {option}", {}) for option in self.addon1.selected_options)
    if self.addon2.name:
        lines.append((line_fmt("  " + self.addon2.name,
                self.addon2.total * bool(addon2[2])), receipt_printer_style["item"]))
        lines.extend((f"    + {option}", {}) for option in self.addon2.selected_options)
    return lines


@log_info("Created new order", time=True)
def NewOrder():
    return OrderInterface("Orders", (Ticket,), {
        "__new__": new,
        "total": total,
        "addon1": addon1,
        "addon2": addon2,
        "__str__":__str__,
        "parameters":parameters,
        "receipt":receipt,
        "printer_style": receipt_printer_style})

def Order():
    if OrderInterface.instance is None:
        return NewOrder()
    return OrderInterface.instance

