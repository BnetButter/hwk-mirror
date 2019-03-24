from operator import itemgetter
from lib import MenuItem
from lib import MenuType
from lib import OrderInterface
from lib import SYS_STDOUT
from lib import log_info
from lib import Ticket
import logging

logger = logging.getLogger(SYS_STDOUT)




def new(cls, menu_item, addon1, addon2, selected_options=None):
    
    param1 = {"register": menu_item.category in cls.register}
    param2 = {"register": addon1.category in cls.register}
    param3 = {"register": addon2.category in cls.register}

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

    if self.category not in type(self).two_sides:
        total += self.addon1.total
        total += self.addon2.total
    return total

parameters = property(itemgetter(5))
addon1 = property(itemgetter(6))
addon2 = property(itemgetter(7))

def __str__(self):
    lines = list()
    lines.append(self.name)
    lines.extend([f"        + {option}" for option in self.selected_options])
    lines.append("    " + self.addon1.name)
    lines.extend([f"        + {option}" for option in self.addon1.selected_options])
    lines.append("    " + self.addon2.name)
    lines.extend([f"        + {option}" for option in self.addon2.selected_options])
    return "\n".join(lines)


@log_info("Created new order", time=True)
def NewOrder():
    return OrderInterface("Orders", (Ticket,), {
        "__new__": new,
        "total": total,
        "addon1": addon1,
        "addon2": addon2,
        "__str__":__str__,
        "parameters":parameters})

def Order():
    if OrderInterface.instance is None:
        return NewOrder()
    return OrderInterface.instance