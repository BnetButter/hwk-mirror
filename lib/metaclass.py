from functools import partial
from collections import UserList
from abc import ABCMeta
from decimal import Decimal
from decimal import ROUND_HALF_DOWN
from operator import itemgetter
from .data import MENUDATA
from .data import CONFIGDATA

class MenuItem(tuple):
    def __new__(self, category, name, price, options):
        return super().__new__(self, (category, name, price, options))
    
    def __eq__(self, other):
        return self[0] == other[0] \
                and self[1] == other[1]
    
    def __bool__(self):
        return self.name != ""
    
    category = property(itemgetter(0))
    name = property(itemgetter(1))
    price = property(itemgetter(2))
    options = property(itemgetter(3))

class MenuType(type):
    """Provides a class with an interface to menu information"""

    def __new__(self, name, bases, attr, *args, **kwargs):
        attr["menu"] = MENUDATA["menu"]
        attr["config"] = MENUDATA["config"]
        return super().__new__(self, name, bases, attr)

    def __init__(self, name, bases, attr, *args, **kwargs):
        items = [self.menu[category].keys() for category in self.menu]
        items = [item for lst in items for item in lst]
        sides = list(self.menu["Sides"].keys())
        sides.extend(list(self.menu["Drinks"].keys()))
        self.categories = sorted([category for category in self.menu], key=len, reverse=True)
        self.longest_item = len(sorted(items, key=len)[-1])
        self.longest_addon = len(sorted(sides, key=len)[-1])
        self.longest_category = len(sorted(self.categories, key=len)[-1])
        self.include_sides = self.config["Sides Included"]
        self.include_drinks = self.config["Drinks Included"]
        self.two_sides = self.config["Two Sides"]
        self.no_addons = self.config["No Addons"]
        self.taxrate = Decimal(self.config["Tax"]).quantize(Decimal('.01'))


    def category(self, category, cls=MenuItem):
        """return a list of menu items"""
        return [
            cls(category, item,
                    self.menu[category][item]["Price"],
                    self.menu[category][item]["Options"])
                for item in self.menu[category]
            ]

    @staticmethod
    def null_item(self, cls=MenuItem):
        return cls("", "", 0, {})

class WidgetType(type):
    """Instance a class with font configuration data"""

    def __new__(cls, name, bases, attr, device, *args, **kwargs):    
        config = CONFIGDATA
        if device not in config.keys() and device is not None:
            raise Exception(f"Missing configurations for '{device}'")

        # default fonts for class
        fonts = [key for key in attr if "font" in key]
        
        # instance must specify some font variable
        if name not in config[device].keys() and not fonts:
            raise Exception(f"Missing configurations for '{name}'")
        elif name not in config[device].keys():
            config[device][name] = dict()
        
        for font in fonts:
            if font in config[device][name]:
                attr[font] = tuple(config[device][name][font])
            else:
                config[device][name][font] = attr[font]
        return super().__new__(cls, name, bases, attr)

class OrderInterface(MenuType, UserList):
    instance = None

    def __new__(cls, name, bases, attr):
        attr["orders"] = list()
        cls.instance = super().__new__(cls, name, bases, attr)
        return cls.instance

    def __str__(self):
        return str(self.data)

    @property
    def data(self):
        return self.orders
    
    @property
    def total(self)->int:
        return sum(ticket.total for ticket in self.orders)
    
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

class TicketType(MenuType, ABCMeta):
    pass