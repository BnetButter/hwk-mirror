from tkinter import ttk
from .order import Order
import collections
import tkinter as tk
import lib
import math
import functools


class _EditOptions(tk.Frame, metaclass=lib.WidgetType, device="POS"):
    font = ("Courier", 16)

    def __init__(self, parent, item, **kwargs):
        super().__init__(parent, **kwargs)
        label = tk.Label(self, font=self.font, text=f"{item.name}")
        self.item = item
        self.options = [lib.ToggleSwitch(self, text=option, font=self.font,) for option in item.options]
        self.grid_columnconfigure(0, weight=1)

        label.grid(row=0, column=0, columnspan=2, sticky="nsw", padx=5, pady=5)
        tk.Label(self, text="    ", font=self.font).grid(row=1, column=0, sticky="nswe")
        for i, option in enumerate(self.options):
            option.grid(row=i+1, column=1, sticky="nswe", padx=5, pady=10, ipadx=5, ipady=5)

    def apply(self):
        self.item.selected_options = (option["text"] for option in self.options if option)


class OptionsEditor(tk.Toplevel, metaclass=lib.ToplevelType):

    def __new__(cls, parent, **kwargs):
        ticket = Order()[-1]
        ticket = ticket, ticket.addon1, ticket.addon2
        ticket = [item for item in ticket if item.options]
        if ticket:
            return super().__new__(cls)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.wm_title("Options")
        ticket = Order()[-1]
        ticket = ticket, ticket.addon1, ticket.addon2

        self.option_editors = [_EditOptions(self, item) for item in ticket if item.options]
        for i, frame in enumerate(self.option_editors):
            frame.grid_columnconfigure((i*2), weight=1)
            frame.grid(row=0, column=i * 2, sticky="nswe")
            

        separators = (ttk.Separator(self, orient=tk.VERTICAL)
            for i in range(len(self.option_editors) - 1))

        for i, separator in enumerate(separators):
            separator.grid(row=0, column=(i * 2) + 1, sticky="ns")

        frame = tk.Frame(self)
        apply = tk.Button(frame, text="Apply", command=self.apply, font=("Courier", 14), bg="green")
        close = tk.Button(frame, text="Close", command=self.destroy, font=("Courier", 14))
        close.pack(side=tk.LEFT, padx=5, pady=5)
        apply.pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Separator(self).grid(row=1, column=0, columnspan=3, sticky="we")
        frame.grid(row=2, column=0, sticky="w")

    def apply(self, *args):
        for editor in self.option_editors:
            editor.apply()
        self.destroy()


class SingletonMenu(lib.SingletonType, lib.MenuType):
    """resolve metaclass conflict"""

# for higher throughput, items will be added to Order sequentially.
# OrderNavigator() uses the first item to decide the next two tabs to lift
# because want to cut down on the amount of taps it takes to complete a set
# of actions.
#
# We also want to closely replicate the order in which a customer may place an order
# so as to minimize cognitive load on the user.
#
# A previous version had drop down menus for "Sides" and "Drinks" addons.
# Adding a Side as an addon would therefore require 2 taps.
# then adding the order itself would take another tap.
# Given the small size of the drop down menu, it was also error prone.
# So this should minimize error and the amount of screen taps needed to
# add an order to the global Order() list

class _OrderNagivator(metaclass=SingletonMenu):
    null = lib.MenuItem("", "", 0, {})

    def __init__(self, tabframe, **kwargs):
        assert isinstance(tabframe, lib.TabbedFrame)
        self.parent = tabframe
        self.counter = 0
        self.select = functools.partial(lib.TabbedFrame.select, tabframe)
        null = type(self).null
        self.items = [null, null, null]

        # these are the only relevant categories.
        # default are item categories that are not in two sides and no addons.
        self.tab_selector = {
            # default | two sides | no addons
            1:["Sides", "Sides",    None],
            2:["Drinks","Sides",    None]
        }

        self.case = 0
        self.current_order_len = 0

    @lib.update
    def update(self):
        if self.current_order_len != len(Order()):
            self.current_order_len = len(Order())
            self.reset()

    def add_item(self, item=null):
        cls = type(self)
        self.items[self.counter] = item

        # decide the next 2 tabs
        if self.counter == 0:
            if item is cls.null:
                return
            Order()(*self.items)
            self.current_order_len += 1
            if item.category in cls.two_sides:
                self.case = 1
            elif item.category in cls.no_addons:
                self.create_ticket()
                return
        
        self.update_ticket()
        self.counter += 1
        try:
            tab = self.tab_selector[self.counter][self.case]
            self.select(tab)
        except:
            self.create_ticket()
    

    def remove_item(self):
        self.items[self.counter] = type(self).null
        self.counter -= 1
        

    def update_ticket(self):
        try:
            Order().pop()
            Order()(*self.items)
        except:
            Order()(*self.items)
    
    def reset(self):
        self.items = [type(self).null for i in range(3)]
        self.counter = 0
        
    def create_ticket(self):
        OptionsEditor(self.parent)
        self.reset()
    
def OrderNavigator(parent=None, **kwargs):
    return _OrderNagivator(parent, **kwargs)



class ItemButton(lib.MessageButton, metaclass=lib.MenuWidget, device="POS"):

    font = ("Courier", 25)
    def __init__(self, parent, item, **kwargs):
        super().__init__(parent, **kwargs)
        self.item = item
        self.configure(font=type(self).font, text=self.item.name)
    
    def set_command(self, orderdisplay, ordertab):
        def command():
            orderdisplay.instance.select(ordertab)
            OrderNavigator().add_item(self.item)
        self.command = command
    

class OpenCharge(tk.Frame, metaclass=lib.MenuWidget, device="POS"):
    
    font=("Courier", 25)

    def __init__(self, parent, category, **kwargs):
        super().__init__(parent, **kwargs)
        self.category = category
        self.price_input = lib.PriceInput(self, 
                font=self.font,
                width=7)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.button = lib.MessageButton(self, text="Open Charge",
                anchor=tk.W, 
                font=self.font,
                relief=tk.RAISED,
                bd=2)
        
        self.button.command = self.add_item
        self.button.grid(row=0, column=0, sticky="nswe")
        self.price_input.grid(row=0, column=1, sticky="nswe")

        self.update()

    def add_item(self):
        price = int(self.price_input.value)
        if price:
            item = self.category, "Open Charge", price, {}
            OrderNavigator().add_item(
                lib.MenuItem(*item))
    
    @lib.update
    def update(self):
        price = int(self.price_input.value)
        if price:
            self.button.activate()
        else:
            self.button.deactivate()


class NullItem(lib.LabelButton, metaclass=lib.WidgetType, device="POS"):
    font=("Courier", 25)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, "None",
                font=type(self).font,
                command=OrderNavigator().add_item,
                **kwargs)
        self.update()


    @lib.update
    def update(self):
        if not OrderNavigator().counter:
            self.deactivate()
        else:
            self.activate()

class CategoryFrame(lib.ScrollFrame, metaclass=lib.MenuType):
    
    def __init__(self, parent, category, **kwargs):
        assert isinstance(parent, lib.TabbedFrame)
        super().__init__(parent, **kwargs)
        self.buttons = [
            ItemButton(self.interior, item,
                    width=200,
                    aspect=150,
                    bd=2, relief=tk.RAISED)

            for item in type(self).category(category)
        ]

        column = 0
        row = 1
        self.none = NullItem(self.interior)
        self.open_charge = OpenCharge(self.interior, category)
        self.none.grid(row=row, column=0, pady=10, padx=10, sticky="nswe")
        self.open_charge.grid(row=row, column=1, columnspan=2, sticky="nswe", pady=10, padx=10)

        for i in range(3):
            self.interior.grid_columnconfigure(i, weight=1)

        for button in self.buttons:
            if column == 3:
                self.interior.grid_rowconfigure(row, weight=1)
                column = 0
                row += 1
                continue
            button.grid(
                    row=row + 1,
                    column=column,
                    sticky="nswe",
                    padx=10,
                    pady=10,
                    ipady=10)
            column += 1
        

    def set_keypress_bind(self, 
            target,
            menudisplay,
            orderdisplay,
            orderdisplay_tab):
        
        def input_condition():
            cond1 = menudisplay.instance.current() == self.open_charge.category
            cond2 = orderdisplay.instance.current() == orderdisplay_tab
            return cond1 and cond2
        
        on_enter = self.open_charge.add_item

        return self.open_charge.price_input.set_keypress_bind(
                target,
                condition=input_condition,
                on_enter=on_enter)

    def set_item_command(self, orderdisplay, tab="Orders"):
        for button in self.buttons:
            button.set_command(orderdisplay, tab)