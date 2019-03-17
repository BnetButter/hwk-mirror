from lib import ScrollFrame
from lib import TabbedFrame
from lib import Order
from lib import WidgetType, MenuWidget
from lib import Ticket
from lib import ToggleSwitch
from lib import AsyncWindow
from lib import update
from lib import write_enable
from functools import partial
from tkinter import ttk
import tkinter as tk
import asyncio
import logging


class OptionLabel(tk.Text, metaclass=MenuWidget, device="POS"):
    font = ("Courier", 12)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, 
            font=self.font,
            width=20,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bg=parent["bg"],
            **kwargs)
    
    @write_enable
    def _update(self, item:Ticket):
        self.delete("1.0", tk.END)
        selected_options = "\n".join([
            f"        + {option}"
                for option in item.selected_options])
        self.insert(tk.END, selected_options)
        self["height"] = len(item.selected_options)

class EditOptions(tk.Toplevel, metaclass=MenuWidget, device="POS"):
    font = ("Courier", 12, "bold")
    
    def __new__(cls, parent, ticket, *args, **kwargs):
        if ticket.options:
            return super().__new__(cls)
        
    def __init__(self, parent, ticket, *args, **kwargs):
        super().__init__(parent, **kwargs)
        self.ticket = ticket
        self.toggles = []
        self.label = tk.Label(self, 
                text=f"Edit options for {ticket.name}",
                font=self.font)
        self.label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")

        longest_option = len(sorted(
                [option for option in ticket.options], 
                key=len)[-1])
        
        for i, option in enumerate(ticket.options):
            toggle = ToggleSwitch(self,
                    option,
                    font=self.font,
                    width=longest_option,
                    state=(option in ticket.selected_options))
            toggle.grid(row=i + 1, column=1, pady=5, padx=5, sticky="nswe")
            self.toggles.append(toggle)
        
        self.protocol("WM_WINDOW_DELETE", self.destroy)
        done = tk.Button(self, text="Done", bg="green", command=self.destroy)
        close = tk.Button(self, text="Close", bg="red", command=super().destroy)
        row = len(self.toggles) + 2
        done.grid(row=row, column=1, pady=10, padx=5, sticky="nswe")
        close.grid(row=row, column=0, pady=10, padx=5, sticky="nswe")

    def destroy(self, *args):
        self.ticket.selected_options = \
                [toggle["text"] for toggle in self.toggles if toggle]
        super().destroy()

    @classmethod
    def call(cls, parent, ticket):
        return partial(cls, parent, ticket)
    
class ItemLabel(tk.Label, metaclass=MenuWidget, device="POS"):

    font = ("Courier", 14, "bold")
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                font=self.font,
                width=ItemLabel.longest_item, # pylint: disable=E1101
                anchor=tk.W,
                **kwargs)
        self._isaddon = True
    
    @property
    def isaddon(self):
        return self._isaddon
    
    @isaddon.setter
    def isaddon(self, value:bool):
        self._isaddon = value

    def _update(self, ticket: Ticket):
        if self.isaddon:
            self["text"] = "    " + ticket.name
        else:
            self["text"] = ticket.name


class PriceButton(tk.Button, metaclass=WidgetType, device="POS"):
    font = ("Courier", 14, "bold")

    def __init__(self, parent, **kwargs):
        super().__init__(parent, 
                font=self.font, 
                relief=tk.FLAT, 
                state=tk.DISABLED,
                width=len("$ 000.00"),
                anchor=tk.W,
                **kwargs)

    def _update(self, ticket):
        assert isinstance(ticket, Ticket)
        if ticket.total > 0:
            self["state"] = tk.ACTIVE
            self["command"] = partial(Order().remove, ticket)
            self["text"] = "$ {:.2f}".format(ticket.total / 100)
            self["relief"] = tk.RAISED
        else:
            self["command"] = lambda: None
            self["text"] = ""
            self["relief"] = tk.FLAT
            self["state"] = tk.DISABLED

class TicketFrame(tk.Frame, metaclass=MenuWidget, device="POS"):

    font = ("Courier", 14)

    get_widgets = lambda parent, **kwargs: (ItemLabel(parent), OptionLabel(parent))
    null_ticket = Ticket(("", "", 0, {}))
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.widgets = [TicketFrame.get_widgets(self) for i in range(3)]

        self.widgets[0][0].isaddon = False
        self.button = PriceButton(self)
        self.button.grid(row=0, column=1, sticky="nswe")

    def _update(self, index):
        try:
            order = Order()[index]
        except IndexError:
            return self.reset()

        [widget._update(order) for widget in self.widgets[0]]
        [widget._update(order.addon1) for widget in self.widgets[1]]
        [widget._update(order.addon2) for widget in self.widgets[2]]

        tickets = order, order.addon1, order.addon2
        for i, widgets in enumerate(self.widgets):
            widgets[0].bind("<Double-Button-1>", EditOptions.call(widgets[0], tickets[i]))

        self._grid_widgets(0, order)
        self._grid_forget(0, order)
        self._grid_widgets(1, order.addon1)
        self._grid_widgets(2, order.addon2)
        self._grid_forget(1, order.addon1)
        self._grid_forget(2, order.addon2)
        self.button._update(order)

    def _grid_widgets(self, index, ticket):
        item, options = self.widgets[index]
        if ticket:
            item.grid(row=index * 2, column=0, sticky="nsw")
        if ticket.selected_options:
            options.grid(row=(index * 2) + 1, column=0, sticky="nsw")
        
    def _grid_forget(self, index, ticket):
        if not ticket:
            [widget.grid_forget() for widget in self.widgets[index]]
        
        if not ticket.selected_options:
            self.widgets[index][1].grid_remove()
        
    def reset(self):
        for item, option in self.widgets:
            item._update(self.null_ticket)
            option._update(self.null_ticket)
        self.button._update(self.null_ticket)
    
class OrdersFrame(ScrollFrame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tickets = []
        
        self.interior.grid_columnconfigure(0, weight=1)
        self.interior.grid_columnconfigure(1, weight=1)
        # prevents window from collapsing on configure
        null_frame = TicketFrame(self.interior)
        null_frame.grid(row=0, column=0, columnspan=2, sticky="nswe")
        null_frame.lower()
        AsyncWindow.append(self.update_order_list)

    @update
    def update_order_list(self):
        if len(self.tickets) < len(Order()):
            self.tickets.append(TicketFrame(self.interior))

        for i, ticket in enumerate(self.tickets):                
            ticket._update(i)
            ticket.grid(row=i, column=0,
                    columnspan=2,
                    padx=5,
                    sticky="we")


