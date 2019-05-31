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



class MenuType(ABCMeta):
    """Provides a class with an interface to menu information"""
    
    menu_items = MENUDATA["menu"]
    menu_config = MENUDATA["config"]

    def __new__(cls, name, bases, attr, *args, **kwargs):
        attr["menu"] = cls.menu_items
        attr["config"] = cls.menu_config
        return super().__new__(cls, name, bases, attr)

    def category_configurations(self):
        return {
            key: self.config[key]
            for key in self.config
                if key != "Payment Types" and key != "Tax"
        }

    def category(self, category, cls=MenuItem):
        """return a list of menu items"""
        if not category or category not in self.menu.keys():
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
    
    # volatile attributes. changes on menu edit
    @property
    def payment_types(self):
        return self.config["Payment Types"]

    @property
    def include_sides(self):
        return self.config["Sides Included"]
    
    @property
    def include_drinks(self):
        return self.config["Drinks Included"]

    @property
    def two_sides(self):
        return self.config["Two Sides"]
        
    @property
    def no_addons(self):
        return self.config["No Addons"]
    
    @property
    def register(self):
        return self.config["Register"]

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
    
class TicketType(MenuType):

    def __init__(self, name, bases, attr, *args, **kwargs):
        self.category = property(itemgetter(0), self.setter(0))
        self.name = property(itemgetter(1), self.setter(1))
        self.price = property(itemgetter(2), self.setter(2))
        self.options = property(itemgetter(3), self.setter(3))
        self.selected_options = property(itemgetter(4), self.set_selected_options)
        self.parameters = property(itemgetter(5), self.setter(5))
        self.addon1 = property(itemgetter(6), self.setter(6))
        self.addon2 = property(itemgetter(7), self.setter(7))
    
    def convert_to(self, category, name, price, options, selected_options, parameters, addon1=None, addon2=None):
        if addon1 is not None and addon2 is not None:
            addon1 = tuple.__new__(self, addon1)
            addon2 = tuple.__new__(self, addon2)
            return tuple.__new__(self, (category,name,price,options,selected_options,parameters, addon1,addon2))
        return tuple.__new__(self, (category,name,price,options,selected_options,parameters))

    @staticmethod
    def compare(self, other) -> (list, int):
        """compare(a, b) -> (list, int)
            returned list is a list of strings
            returned int is a count of differences"""
            
        differences = []
        if (len(self) != 8 or len(other) != 8) and len(self) == len(other):
            raise ValueError("no addons for comparison")

        a = self, self[6], self[7]
        b = other, other[6], other[7]

        no_changes = "{}".format
        changed_to = "{} -> {}".format
        removed = "{} (removed)".format
        added = "{} (added)".format

        change_count = 0
        for i, (a, b) in enumerate(zip(a, b)):
            if a.name and not b.name:
                if i:
                    differences.append("  " + removed(a.name))
                else:
                    differences.append(removed(a.name))
                change_count += 1
                
            elif b.name and not a.name:
                if i:
                    differences.append("  " + added(b.name))
                else:
                    differences.append(added(b.name))
                change_count += 1
            

            elif (a.name and b.name) and a.name != b.name:
                if i:
                    differences.append("  " + changed_to(a.name, b.name))
                else:
                    differences.append(changed_to(a.name, b.name))
                change_count += 1

            elif (a.name and b.name) and a.name == b.name:
                if i:
                    differences.append("  " + no_changes(a.name))
                else:
                    differences.append(no_changes(a.name))
        
        for line in differences:
            if len(line) > 34:
                line.replace("->", "\n    -> ")

        return differences, change_count

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


class WidgetType(ABCMeta):
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
class OrderInterface(TicketType, MenuType, UserList):
    instance = None

    def __new__(cls, name, bases, attr, *args, **kwargs):
        attr["data"] = list()
        cls.instance = super().__new__(cls, name, bases, attr)
        return cls.instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = list()

    def __str__(self):
        lines = list()
        for ticket in self.data:
            lines.append(str(ticket))
        return "\n".join(lines)

    def remove(self, item):
        for i, order in enumerate(self.data):
            if item is order:
                return self.pop(i)

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


class ToplevelType(type):
    """Centers toplevel window"""

    @staticmethod
    def center(result):
        screen_center_X, screen_center_Y = (            
                int(result.winfo_screenwidth() / 2),
                int(result.winfo_screenheight() / 2))

        widget_center_X, widget_center_Y = tuple(
                int(int(dim) / 2) for dim in result.geometry().split("+")[0].split("x"))
        x, y = (
            screen_center_X - widget_center_X,
            screen_center_Y - widget_center_Y)
        result.geometry(f"+{x}+{y}")
        return result

    def __call__(self, *args, **kwargs):
        result = super().__call__(*args, **kwargs)
        if result is not None:
            result.attributes("-topmost", True)
            return self.center(result)
        
# resolve metaclas conflict
class MenuWidget(WidgetType, MenuType): ...


class ToplevelWidget(MenuWidget, ToplevelType):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ToplevelType.__init__(self, *args, **kwargs)


class ReinstanceType(MenuWidget):
    objects = list()
    null_method = lambda:None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance = None
    
    @property
    def instance(self):
        return self._instance
    
    @instance.setter
    def instance(self, value):
        self._instance = value
    
    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
            type(self).objects.append((self, args, kwargs))
            return self.instance
        
        grid_info = self.instance.grid_info()
        grid_info.pop("in")
        assert hasattr(self.instance, "children")
        if hasattr(self.instance, "dtor"):
            self.instance.dtor()
        for c in list(self.instance.children.values()):
            c.destroy()
        self.instance.__init__(*args, **kwargs)
        if hasattr(self.instance, "ctor"):
            self.instance.ctor
        self.instance.grid(**grid_info)
        return self.instance
    
    @classmethod
    def reinstance(cls, target=None):    
        if target is None:
            for cls, args, kwargs in cls.objects:
                return cls(*args, **kwargs)
        else:
            for cls, args, kwargs in cls.objects:
                if target == cls:
                    return cls(*args, **kwargs)
        
                
class SingletonType(type):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance

