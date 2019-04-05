from functools import partial
from functools import wraps
from collections import UserList
from abc import ABCMeta
from abc import abstractmethod
from decimal import Decimal
from decimal import ROUND_HALF_DOWN
from operator import itemgetter
from .data import MENUDATA
from .data import CONFIGDATA
from .data import GUI_STDOUT
import tkinter as tk
import asyncio
import websockets
import logging

class MenuItem(tuple):
    def __new__(cls, category, name, price, options):
        return super().__new__(cls, (category, name, price, options))
    
    def __eq__(self, other):
        return self[0] == other[0] \
                and self[1] == other[1]
    
    def __bool__(self):
        return self.name != ""
    
    category = property(itemgetter(0))
    name = property(itemgetter(1))
    price = property(itemgetter(2))
    options = property(itemgetter(3))

class TicketType(ABCMeta):

    def __init__(self, name, bases, attr):
        self.category = property(itemgetter(0), self.setter(0))
        self.name = property(itemgetter(1), self.setter(1))
        self.price = property(itemgetter(2), self.setter(2))
        self.options = property(itemgetter(3), self.setter(3))
        self.selected_options = property(itemgetter(4), self.set_selected_options)
        self.parameters = property(itemgetter(5), self.setter(5))
        
    @staticmethod
    def setter(index):
        def _setter(self, value):
            self[index] = value
        return _setter

    @staticmethod
    def set_selected_options(self, iterable):
            self.selected_options.clear()
            self.selected_options.extend(iterable)
    

class Ticket(MenuItem, metaclass=TicketType):

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

class MenuType(type):
    """Provides a class with an interface to menu information"""
    
    menu_items = MENUDATA["menu"]
    menu_config = MENUDATA["config"]

    def __new__(cls, name, bases, attr, *args, **kwargs):
        attr["menu"] = cls.menu_items
        attr["config"] = cls.menu_config
        return super().__new__(cls, name, bases, attr)

    def __init__(self, name, bases, attr, *args, **kwargs):
        self.include_sides = self.config["Sides Included"]
        self.include_drinks = self.config["Drinks Included"]
        self.two_sides = self.config["Two Sides"]
        self.no_addons = self.config["No Addons"]
        self.register = self.config["Register"]
        self.payment_types = self.config["Payment Types"]
    
    def category(self, category, cls=MenuItem):
        """return a list of menu items"""
        if not category:
            return []

        return [
            cls(category, item,
                    self.menu[category][item]["Price"],
                    self.menu[category][item]["Options"])
                for item in self.menu[category]
            ]

    @staticmethod
    def get_item(category, name):
        price = MenuType.menu_items[category][name]["Price"]
        options = MenuType.menu_items[category][name]["Options"]
        return MenuItem(category, name, price, options)

    @staticmethod
    def null_item(self, cls=MenuItem):
        return cls("", "", 0, {})
    
    # volatile attributes
    @property
    def all_item_names(self):
        items = [self.menu[category].keys() for category in self.menu]
        return [item for lst in items for item in lst]

    @property
    def all_addon_names(self):
        sides = list(self.menu["Sides"].keys())
        sides.extend(list(self.menu["Drinks"].keys()))
        return sides

    @property
    def categories(self):
        return sorted([category for category in self.menu], key=len, reverse=True)
    
    @property
    def longest_item(self):
        return len(sorted(self.all_item_names, key=len)[-1])
    
    @property
    def longest_addon(self):
        return len(sorted(self.all_addon_names, key=len)[-1])

    @property
    def longest_category(self):
        return len(sorted(self.categories, key=len)[-1])

    @property
    def taxrate(self):
        return Decimal(self.config["Tax"]).quantize(Decimal('.01'))
    

class WidgetType(type):
    """Instance a class with font configuration data"""

    def __new__(cls, name, bases, attr, device, *args, **kwargs):    
        config = CONFIGDATA
        if device not in config.keys() and device is not None:
            raise Exception(f"Missing configurations for '{device}'")

        # default fonts for class
        fonts = [key for key in attr if "font" in key or "config" in key]
        
        # instance must specify some font variable
        if name not in config[device].keys() and not fonts:
            raise Exception(f"Missing font configurations for '{name}'")
        elif name not in config[device].keys():
            config[device][name] = dict()
        
        for font in fonts:
            if font in config[device][name]:
                attr[font] = tuple(config[device][name][font])
            else:
                config[device][name][font] = attr[font]
        return super().__new__(cls, name, bases, attr)


# OrderInterface creates a singleton class accessed by calling lib.Order()
# calling lib.NewOrder() replaces the instance with a new list

class OrderInterface(MenuType, UserList, TicketType):
    instance = None

    def __new__(cls, name, bases, attr):
        attr["data"] = list()
        cls.instance = super().__new__(cls, name, bases, attr)
        return cls.instance

    def __str__(self):
        lines = list()
        for ticket in self.data:
            lines.append(str(ticket))
        return "\n".join(lines)

    def remove(self, item):
        super().remove(item)
        
    @property
    def total(self)->int:
        return sum(ticket.total for ticket in self.data)
    
    @property
    def subtotal(self)->int:
        tax_scale = int((self.taxrate * 100) + 10000)
        result = Decimal((self.total * 100) 
                / tax_scale).quantize(
                    Decimal('0.01'),
                        rounding=ROUND_HALF_DOWN)
        return int(result * 100)

    @property
    def tax(self)->int:
        return self.total - self.subtotal

# resolve metaclas conflict
class MenuWidget(WidgetType, MenuType):
    pass

