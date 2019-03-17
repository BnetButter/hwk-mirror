from operator import itemgetter
from .metaclass import MenuItem
from .metaclass import MenuType
from .metaclass import OrderInterface
from .data import SYS_STDOUT
from .data import log_info
import logging

logger = logging.getLogger(SYS_STDOUT)

class Ticket(MenuItem):

    def __new__(cls, menu_item, selected_options=None, parameters={}):
        
        if selected_options is None:
            return tuple.__new__(cls, (*menu_item, list(), parameters))
        else:
            assert all(option in menu_item[3] for option in selected_options)
            return tuple.__new__(cls, (*menu_item, list(selected_options), parameters))
    
    def __bool__(self):
        return self.total > 0

    @property
    def total(self):
        total = self.price
        for option in self.selected_options:
            total += self.options[option]
        return total

    @property
    def selected_options(self):
        return self[4]
    
    @selected_options.setter
    def selected_options(self, value):
        assert all(option in self.options.keys() for option in value)
        self.selected_options.clear()
        self.selected_options.extend(value)

    parameters = property(itemgetter(5))


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