from lib import ScrollFrame
from lib import TabbedFrame
from lib import Ticket
from lib import WidgetType, MenuWidget, ToplevelWidget
from lib import ToggleSwitch
from lib import AsyncTk, update
from lib import write_enable
from .order import Order, ORDER_EDIT, ORDER_SELECT, ModeController
from .options import EditOptions
from functools import partial
from tkinter import ttk
import lib
import tkinter as tk
import asyncio
import logging
import collections
import functools


# this class is a tk.Entry instance because it has a highlight border.
# when selected, this widget specifies where to change the Order() entries.
# Allows the Order() list to be modified on-the-fly.
class ItemLabel(tk.Entry):

    def __init__(self, parent, subindex, **kwargs):
        # relief, bg, insertbackground hides its... Entryness.
        super().__init__(parent,
                text="",            
                relief=tk.FLAT, 
                bg=parent["bg"],
                insertbackground=parent["bg"],
                highlightcolor="red",
                state="readonly", 
                selectbackground=parent["bg"], # so text doesn't have a highlight box
                width=Order.longest_item,
                **kwargs)
        self._text = tk.StringVar(self)
        self.configure(textvariable=self._text)
        self.selected = False
        self.subindex = subindex
        self.index = None
        self.bind("<Button-1>", self.on_press)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
   
    def remove_highlight(self):
        # an item was added to this widget's location
        self.master["relief"] = tk.FLAT
    
    def highlight(self):
        self.master["relief"] = tk.RIDGE

    def on_focus_in(self, event):
        ModeController().select(self.index, self.subindex)
        self.selected = True
    
    def on_focus_out(self, event):
        ModeController().unselect()
        self.selected = False

    def on_press(self, *event):
        if self.selected:
            self.event_generate("<FocusOut>")
        else:
            self.event_generate("<FocusIn>")
    
    def update(self, item, index):
        self.index = index
        if item.name:
            text = "    " + item.name if self.subindex else item.name
        else:
            text = "    " + "(null)" if self.subindex else "(null)"
        self._text.set(text)


class OptionLabel(tk.Label):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, 
            justify=tk.LEFT,
            bd=2,
            **kwargs)
    
    def update(self, item):
        
        comments = item.parameters.get("comments", "")
        comments = "     " + f"'{comments}'" + "\n" if comments else ""
        
        if item.selected_options or comments:
            self["text"] = comments + "\n".join(
                    "      + " + opt
                    for opt in item.selected_options)
            self.grid()
        else:
            self.grid_remove()


class PriceButton(lib.LabelButton):

    fmt = "$ {:.2f}".format

    def __init__(self, master, **kwargs):
        super().__init__(master, "Options", 
                bd=2, width=8,
                relief=tk.FLAT, anchor=tk.CENTER,
                **kwargs)

    def is_included(self):
        self["relief"] = tk.RAISED
        self["text"] = "$ 0.00"

    def update(self, item):
        price = item.price + sum(item.options.get(opt, 0) for opt in item.selected_options)
        if item.name:
            self["relief"] = tk.RAISED
            self["text"] = type(self).fmt(price / 100)
        else:
            self["relief"] = tk.FLAT
            self["text"] = ""

    
class OptionButton(lib.LabelButton):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                 text="", bd=2,
                 width=8, relief=tk.FLAT,
                 anchor=tk.CENTER, **kwargs)
        self.command = self._command
        self.item = None
    
    def update(self, item):
        self.item = item
        self["text"] = "Options" if item.name else ""
        if item.name:
            self.activate()
            self["relief"] = tk.RAISED
        else:
            self.deactivate()
            self["relief"] = tk.FLAT

    def _command(self):
        EditOptions(self, self.item)


class ItemFrame(tk.Frame):

    def __init__(self, master, subindex, font=None, **kwargs):
        super().__init__(master, bd=2, **kwargs)
        self.font = font
        self.subindex = subindex
        self.index = None

        self.grid_columnconfigure(0, weight=1)
        self.item_label = ItemLabel(self, subindex, font=font)
        self.option_label = OptionLabel(self, font=font)
        self.price_button = PriceButton(self, font=font, command=self.on_remove)
        self.option_button = OptionButton(self, font=font)

        self.item_label.grid(row=0, column=0, sticky="nw", ipady=2, ipadx=2)
        self.option_button.grid(row=0, column=1, sticky="nw", padx=2, pady=2)
        self.option_label.grid(row=1, column=0, sticky="nw")
        self.price_button.grid(row=0, column=2, sticky="ne", padx=2, pady=2)
        
        ModeController().append(self.item_label)

    def on_remove(self):
        assert self.index is not None
        if self.subindex == 0:
            Order().pop(self.index)
        else:
            Order().set(self.index, self.subindex, lib.NULL_TICKET_ITEM)
        self.item_label.event_generate("<FocusOut>")

    def update(self, index):
        if self.index is None:
            self.index = index

        item = Order().get(index, self.subindex)
        self.item_label.update(item, index) 
        self.option_button.update(item)
        self.option_label.update(item)
        self.price_button.update(item)

    def is_included(self):
        self.price_button["relief"] = tk.RAISED
        self.price_button["text"] = "$ 0.00"


class TicketFrame(tk.Frame, metaclass=WidgetType, device="POS"):
    font = ("Courier", 15)

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.item = ItemFrame(self, 0, font=self.font)
        self.addon1 = ItemFrame(self, 1, font=self.font)
        self.addon2 = ItemFrame(self, 2, font=self.font)

        self.item.grid(row=0, column=0, sticky="nwe")
        self.addon1.grid(row=1, column=0, sticky="nwe") 
        self.addon2.grid(row=2, column=0, sticky="nwe")


    def update(self, index):
        item =  Order()[index]
        if item.category in Order.no_addons:
            self.addon1.grid_remove()
            self.addon2.grid_remove()
        else:
            self.addon1.grid()
            self.addon2.grid()
        
        self.item.update(index)
        self.addon1.update(index)
        self.addon2.update(index)

        if item.category in Order.two_sides:
            self.addon1.is_included()
            self.addon2.is_included()
        elif item.category in Order.include_drinks:
            if item.addon1.category == "Drinks":
                self.addon1.is_included()
            elif item.addon2.category == "Drinks":
                self.addon2.is_included()
        elif item.category in Order.include_sides:
            if item.addon1.category == "Sides":
                self.addon1.is_included()
            elif item.addon2.category == "Sides":
                self.addon2.is_included()

            





class OrdersFrame(ScrollFrame):

    def __init__(self, parent, widgettype=None):
        super().__init__(parent)
        if widgettype is None:
            widgettype = TicketFrame
        self.tickets = lib.WidgetCache(widgettype, self.interior)
        ModeController(self.tickets.data)
        self.interior.grid_columnconfigure(0, weight=1)
        self.interior.grid_columnconfigure(1, weight=1)
        

    @update
    def update_order_list(self):
        order_list = Order()
        order_size = len(order_list)
        self.tickets.realloc(order_size)
        cache_size = len(self.tickets)
        
        for i in range(order_size):
            self.tickets[i].update(i)
            self.tickets[i].grid(row=i, column=0,
                    columnspan=2,
                    padx=5,
                    sticky="nwe",
                    pady=2)
        
        # remove cached widgets
        for widget in self.tickets[order_size:cache_size]:
            widget.grid_remove()

