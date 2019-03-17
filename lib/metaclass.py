from functools import partial
from functools import wraps
from collections import UserList
from abc import ABCMeta
from decimal import Decimal
from decimal import ROUND_HALF_DOWN
from operator import itemgetter
from .data import MENUDATA
from .data import CONFIGDATA
from .stream import stdout, stderr
import tkinter as tk
import asyncio
import websockets
import logging

logger = logging.getLogger("gui")

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

class OrderInterface(MenuType, UserList):
    instance = None

    def __new__(cls, name, bases, attr):
        attr["orders"] = list()
        cls.instance = super().__new__(cls, name, bases, attr)
        return cls.instance

    def __str__(self):
        lines = list()
        for ticket in self.orders:
            lines.append(str(ticket))
        return "\n".join(lines)

    def complete(self):
        pass

    def remove(self, item):
        super().remove(item)
        logger.info(f"Removed ticket: {item.name, item.addon1.name, item.addon2.name}")
    
    def to_dict(self):
        pass

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

class AsyncWindowType(type, UserList):
    """Create a singleton async tkinter.Tk class"""            
    instance = None

    def __new__(cls, name, bases, attr, refresh=None, *args, **kwargs):
        return super().__new__(cls, name, (tk.Tk,), attr)
        
    def __init__(self, name, bases, attr, refresh=None, *args, **kwargs):
        super().__init__(name, bases, attr, *args, **kwargs)
        self.data = list()
        self.update_tasks = list()
        self.loop = asyncio.get_event_loop()
        if refresh is None:
            refresh = 60
        elif not isinstance(refresh, int):
            raise TypeError(f"Expected {int} as 'refresh' argument. Got {type(refresh)} instead.")
        self.interval = 1 / refresh

    def append(self, coroutine, *args, **kwargs):
        coroutine = self.loop.create_task(
                coroutine(*args, **kwargs))
        self.data.append(coroutine)
    
    def add_update_task(self, func):
        self.update_tasks.append(func)
    

    def update_function(self, func):
        assert not asyncio.iscoroutinefunction(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.update_tasks.append(partial(func, *args, **kwargs))
        return wrapper

    def async_update_task(self, func):
        assert asyncio.iscoroutinefunction(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func = self.loop.create_task(
                    func(*args, **kwargs))
            self.data.append(func)
        return wrapper

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance
    
    def exit(self):
        if self.instance is not None:
            self.instance.destroy()


class ServerInterface(ABCMeta, type):

    instance = None
    connect = websockets.connect(f"ws://{CONFIGDATA['ip']}:{CONFIGDATA['port']}")

    def __new__(cls, name, bases, attr):
        if cls.instance is None:
            cls.instance = super().__new__(cls, name, bases, attr)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.serve = partial(self._serve, ip=CONFIGDATA["ip"], port=CONFIGDATA["port"])

    def _serve(self, handler, ip=None, port=None):
        return websockets.serve(handler, ip, port)

# resolve metaclas conflict
class MenuWidget(WidgetType, MenuType):
    pass

class TicketType(MenuType, ABCMeta):
    pass