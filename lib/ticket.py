from operator import itemgetter
from .metaclass import MenuItem
from .metaclass import MenuType
from .metaclass import OrderInterface
import logging

logger = logging.getLogger("gui")

class Ticket(MenuItem):

    def __new__(cls, menu_item, selected_options=None):
        if selected_options is None:
            return tuple.__new__(cls, (*menu_item, list()))
        else:
            assert all(option in menu_item[3] for option in selected_options)
            return tuple.__new__(cls, (*menu_item, list(selected_options)))

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

def new(cls, menu_item, addon1, addon2, selected_options=None):
    addon1 = Ticket(addon1)
    addon2 = Ticket(addon2)

    if selected_options is None:
        cls.data.append(tuple.__new__(cls, (*menu_item, list(), addon1, addon2)))
    else:
        assert all(option in menu_item[3] for option in selected_options)
        cls.data.append(tuple.__new__(cls, (*menu_item,
            selected_options,
            addon1,
            addon2)))

    logger.debug(f"Added ticket {menu_item.name, addon1.name, addon2.name}")

@property
def total(self):
    total = self.price
    for option in self.selected_options:
        total += self.options[option]

    if self.category not in type(self).two_sides:
        total += self.addon1.total
        total += self.addon2.total
    return total

addon1 = property(itemgetter(5))
addon2 = property(itemgetter(6))

def NewOrder():
    logger.info("Created new Order...")
    return OrderInterface("Orders", (Ticket,), {
        "__new__": new,
        "total": total,
        "addon1": addon1,
        "addon2": addon2})

def Order():
    if OrderInterface.instance is None:
        return NewOrder()
    return OrderInterface.instance