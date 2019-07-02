from tkinter import ttk
from .order import Order, ModeController, ORDER_EDIT, ORDER_SELECT
import collections
import tkinter as tk
import lib
import math
import functools

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


def OrderNavigator(parent=None, **kwargs):
    return ModeController(tabframe=parent)


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
                width=7,
                conditional_bind=False)
        self.price_input.configure(state=tk.NORMAL)
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


    def add_item(self):
        price = int(self.price_input.value)
        item = self.category, "Open Charge", price, {}, "", 0
        OrderNavigator().add_item(
            lib.MenuItem(*item))
    



class NullItem(lib.LabelButton, metaclass=lib.WidgetType, device="POS"):
    font=("Courier", 25)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, "None",
                font=type(self).font,
                command=OrderNavigator().add_item,
                **kwargs)
        self.update_func = self.update()
    
    def destroy(self):
        lib.AsyncTk().remove(self.update_func)
        super().destroy()
    
    @lib.update
    def update(self):
        num = OrderNavigator().counter
        if num == 0 or num == 3:
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

