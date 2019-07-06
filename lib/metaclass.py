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

class MenuItemType(ABCMeta):
    __attributes = ("category", "name", "price", "options", "alias", "hidden")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getproperty = lambda index: property(itemgetter(index), self.setx(index))
        self.category = getproperty(0)
        self.name = getproperty(1)
        self.price = getproperty(2)
        self.options = getproperty(3)
        self.alias = getproperty(4)
        self.hidden = getproperty(5)

    @staticmethod
    def setx(index):
        def _(self, value):
            self[index] = value
        return _
    
    @staticmethod
    def getx(index):
        def _(self):
            return self[index]
        return _
        

class SingletonType(ABCMeta):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance


class MenuItem(tuple, metaclass=MenuItemType):

    def __new__(cls, category, name, price, options, alias, hidden):
        return super().__new__(cls, (category, name, price, options, alias, hidden))
    
    def __eq__(self, other):
        return self[0] == other[0] \
                and self[1] == other[1]
    
    def __bool__(self):
        return self.name != ""



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
                    self.menu[category][item]["Options"],
                    self.menu[category][item]["alias"],
                    self.menu[category][item]["hidden"])
                for item in self.menu[category]
            ]

    @staticmethod
    def get_item(category, name):
        price = MenuType.menu_items[category][name]["Price"]
        options = MenuType.menu_items[category][name]["Options"]
        alias = MenuType.menu_items[category][name]["alias"]
        hidden = MenuType.menu_items[category][name]["hidden"]
        return MenuItem(category, name, price, options, alias, hidden)

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


class TicketType(MenuItemType, MenuType):

    def __init__(self, name, bases, attr, **kwargs):
        super().__init__(name, bases, attr, **kwargs)
        self.selected_options = property(itemgetter(6), self.set_selected_options)
        self.parameters = property(itemgetter(7), self.setter(7))
        self.addon1 = property(itemgetter(8), self.setter(8))
        self.addon2 = property(itemgetter(9), self.setter(9))
        self.menu_base = property(self._menu_base)
    
    @staticmethod
    def _menu_base(self):
        return MenuItem(self.category, self.name, self.price, self.options, self.alias, self.hidden)

    def split(self, item, cls=list):
        addon1, addon2 = item.addon1, item.addon2
        item = self.convert_to(*item[:-2])
        return cls((item, addon1, addon2))
    
    def join(self, item, addon1, addon2):
        return self.convert_to(*item, addon1=addon1, addon2=addon2)

    def convert_to(self, category, name, price, options, alias, hidden, selected_options, parameters, addon1=None, addon2=None):
        if addon1 is not None and addon2 is not None:
            addon1 = tuple.__new__(self, addon1)
            addon2 = tuple.__new__(self, addon2)
            return tuple.__new__(self, (category,name,price,options,
                alias,hidden,selected_options,parameters, addon1,addon2))
        return tuple.__new__(self, (category,name,price,options,
                alias,hidden,selected_options,parameters))

    def to_list(self, ticket):
        addon1 = list(ticket.addon1)
        addon2 = list(ticket.addon2)
        ticket = list(ticket)
        ticket[-2] = addon1
        ticket[-1] = addon2
        return ticket

    @staticmethod
    def compare(self, other) -> (list, int):
        """compare(a, b) -> (list, int)
            returned list is a list of strings
            returned int is a count of differences"""
        differences = []
        if (len(self) != 10 or len(other) != 10):
            raise ValueError(f"Invalid comparison {len(self)}, {len(other)}")

        a = self, self.addon1, self.addon2
        b = other, other.addon1, other.addon2
        no_changes = "{}".format
        changed_to = "{} -> {}".format
        removed = "{} (removed)".format
        added = "{} (added)".format

        add_option = "    + {} (added)".format
        remove_option = "    + {} (removed)".format

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

                if a.selected_options == b.selected_options:
                    if i:
                        differences.append("  " + no_changes(a.name))
                    else:
                        differences.append(no_changes(a.name))
                else:
                    added_str = "\n".join(add_option(option) for option in b.selected_options
                                if option not in a.selected_options)
                    removed_str = "\n".join(remove_option(option) for option in a.selected_options
                                if option not in b.selected_options)
                    no_change_str = "\n".join("    + {}".format(option) for option in a.selected_options
                            if option in b.selected_options)


                    changes = "\n".join(string for string in (no_change_str, added_str, removed_str) if string)
                    if changes:
                        changes = "\n" + changes
                
                    if i:
                        differences.append("  " + no_changes(a.name) + changes)
                    else:
                        differences.append(no_changes(a.name) + changes)

                    change_count += 1

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
    
    @staticmethod
    def set_alias(index):
        def _setx(self, value):
            self[index]["alias"] = value
        return _setx
    
    @staticmethod
    def get_alias(index):
        def getx(self):
            return self[index]["alias"]
        return getx
    
    @staticmethod
    def get_parameter(string):
        def getp(self):
            return self[5][string]
        return getp
    
    @staticmethod
    def set_parameter(string):
        def setp(self, value):
            self[5][string] = value
        return setp


class Ticket(MenuItem, metaclass=TicketType):

    def __new__(cls, menu_item, selected_options=[], parameters={}):
        return tuple.__new__(cls, (*menu_item, selected_options, parameters))

    def __bool__(self):
        return bool(self.name)

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


class OrdersType(MenuType, SingletonType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total = property(self._total)
        self.subtotal = property(self._subtotal)
        self.tax = property(self._tax)
    
    @staticmethod
    def _total(self)->int:
        return sum(ticket.total for ticket in self.data)
    
    @staticmethod
    def _subtotal(self)->int:
        tax_scale = int((self.taxrate * 100) + 10000)
        result = Decimal((self.total * 100) 
                / tax_scale).quantize(
                    Decimal('0.01'),
                        rounding=ROUND_HALF_DOWN)
        return int(result * 100)

    @staticmethod
    def _tax(self)->int:
        return self.total - self.subtotal

    @staticmethod
    def _taxrate(self):
        return type(self).taxrate



    
# resolve metaclas conflict
class MenuWidget(WidgetType, MenuType): ...

class ToplevelWidget(MenuWidget):
    """Centers toplevel window"""

    @staticmethod
    def center(result):
        result.update()
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
        assert hasattr(self.instance, "children")
        if hasattr(self.instance, "dtor"):
            self.instance.dtor()
        for c in list(self.instance.children.values()):
            c.destroy()
        self.instance.__init__(*args, **kwargs)
        if hasattr(self.instance, "ctor"):
            self.instance.ctor()

        if "in" in grid_info:
            grid_info.pop("in")    
            self.instance.grid(**grid_info)
        return self.instance
    
    @classmethod
    def reinstance(cls, target=None):
        if target is None:
            for cls, args, kwargs in cls.objects:
                cls(*args, **kwargs)
        else:
            for cls, args, kwargs in cls.objects:
                if target == cls:
                    cls(*args, **kwargs)
    
        
                



class SingletonMenu(MenuType, SingletonType):
    ...

class SingletonWidget(WidgetType, SingletonType):
    ...