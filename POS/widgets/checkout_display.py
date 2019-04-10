# OrderDisplay child widget.
# "CheckoutFrame" is the scrollable container class for change calculator,
#      buttons specifying payment method, and an overview of "Orders" tab.

from lib import ScrollFrame
from lib import MenuWidget
from lib import WidgetType
from lib import ToggleSwitch
from lib import LabelButton
from lib import ToplevelWidget
from lib import NumpadKeyboard
from lib import AsyncTk, update
from .order import Ticket, Order
from .order_display import ItemLabel
from .order_display import TicketFrame
from .order_display import OrdersFrame
from functools import partial
import tkinter as tk
import asyncio
import decimal
import logging

logger = logging.getLogger()

class RegisterButton(ToggleSwitch, metaclass=WidgetType, device="POS"):
    """Indicates where the ticket is to be fulfilled. An active 'register' button
       means that the item on the ticket is to be fulfilled at the register."""

    font=("Courier", 12)


    def _update(self, ticket):
        # during initiation, ticket.parameters is given a boolean type.
        register = ticket.parameters["register"]
        
        # we want to be able to set the state to the default value
        # while also being able to change the state's value.
        if isinstance(register, bool):
            # self.state is slaved to default "register" value.
            self.state = ticket.parameters["register"] = int(register)
        else:
            # this block is executed after the first cycle.
            # now the "register" value is slaved to self.state.
            ticket.parameters["register"] = self.state

class CheckoutLabel(tk.Frame, metaclass=MenuWidget, device="POS"):
    font = ("Courier", 14)
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.checkbutton = RegisterButton(self, "register")
        self.label = tk.Label(self, font=self.font, width=CheckoutLabel.longest_item, anchor="w")
        self.checkbutton.grid(row=0, column=0, padx=5, pady=2)
        self.label.grid(row=0, column=1, pady=2)
        self._isaddon = None
        self.isaddon = True
    
    @property
    def isaddon(self):
        return self._isaddon
    
    @isaddon.setter
    def isaddon(self, value):
        self._isaddon = value

    def _update(self, ticket):
        self.checkbutton._update(ticket)
        if self.isaddon:
            self.label["text"] = "    " + ticket.name
        else:
            self.label["text"] = ticket.name

class CheckoutTicketFrame(tk.Frame):
    null_ticket = Ticket(("", "", 0, {}))

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.widgets = [
            CheckoutLabel(self) for i in range(3)]
        self.widgets[0].isaddon = False
    
    def _grid_widgets(self, index, ticket):
        item = self.widgets[index]
        if ticket:
            item.grid(row=index, column=0, columnspan=2, sticky="w")
    
    def _grid_forget(self, index, ticket):
        item = self.widgets[index]
        if not ticket:
            item.grid_forget()

    def _update(self, order):
        tickets = order, order.addon1, order.addon2
      
        for i, ticket in enumerate(tickets):
            self.widgets[i]._update(ticket)
            self._grid_widgets(i, ticket)
            self._grid_forget(i, ticket)

    def reset(self):
        for widget in self.widgets:
            widget._update(self.null_ticket)

class Numpad(tk.Toplevel, metaclass=ToplevelWidget, device="POS"):
    font=("Courier", 20)
    
    def __init__(self, parent, target, *args, **kwargs):
        super().__init__(parent, **kwargs)
        self.title(string="Num Pad")
        self.numpad = NumpadKeyboard(self, font=self.font, bd=5, relief=tk.RAISED)
        self.numpad.pack(fill=tk.BOTH)
        self.numpad.target = target
        self.parent = parent
      
    def destroy(self, *args):
        self.parent.focus_set()
        super().destroy()

class ChangeCalculator(tk.Frame, metaclass=WidgetType, device="POS"):
    font = ("Courier", 16)
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.cash_given = tk.StringVar(self)
        self.change_due = tk.StringVar(self)
        
        cash_given_frame = self.labeled_entry("Cash Given ", self.cash_given, state=tk.NORMAL)
        change_due_frame = self.labeled_entry("Change Due ", self.change_due)
        cash_given_frame.grid(row=0, column=0, columnspan=2, sticky="nswe")
        change_due_frame.grid(row=1, column=0, columnspan=2, sticky="nswe")
    
    @property
    def cash(self):
        try:
            result = self.cash_given.get().strip()
            result = decimal.Decimal(result).quantize(decimal.Decimal('.01'))
            return int(result * 100)
        except:
            return 0
    
    @property
    def change(self):
        try:
            result = self.change_due.get().strip()
            result = decimal.Decimal(result).quantize(decimal.Decimal('.01'))
            return int(result * 100)
        except:
            return 0
    
    def labeled_entry(self, text, variable, state=tk.DISABLED, **kwargs):
        frame = tk.Frame(self, **kwargs)
        label = tk.Label(frame, font=self.font, text=text)
        entry = tk.Entry(frame, 
                font=self.font,
                textvariable=variable,
                state=state,
                width=10,
                disabledbackground="white",
                disabledforeground="black")
        
        entry.bind("<FocusIn>", partial(Numpad, self, entry))
        
        label.grid(row=0, column=0, sticky="nse")
        entry.grid(row=0, column=1, sticky="nsw")
        return frame

    @update
    def update(self):
        change = Order().total - self.cash
        if change > 0 or Order().total == 0:
            self.change_due.set("- - -")
        else:
            self.change_due.set("{:.2f}".format(change / 100))
            


class ConfirmationWindow(tk.Toplevel, metaclass=ToplevelWidget, device="POS"):
    font=("Courier", 12)

    __slots__ = ["payment_type", "textbox"]
    instance = None

    def __init__(self, parent, payment_type, cash, change, **kwargs):
        super().__init__(parent, **kwargs)
        self.title("Confirm Ticket")
        self.payment_type = payment_type
        self.textbox = tk.Text(self, font=self.font, 
                width=40,
                height=10,
                state=tk.DISABLED,
                bg="grey26",
                fg="white")

        
        def on_confirm():
            AsyncTk().forward("new_order", self.payment_type, cash, change)
            self.destroy()

        frame = tk.Frame(self, relief=tk.RIDGE, bd=2)
        close = tk.Button(frame, text="Close", bg="red", command=self.destroy)
        confirm = tk.Button(frame, text="Confirm", bg="green", command=on_confirm)


        label = tk.Label(self, text=payment_type, font=self.font)
        label.grid(row=0, column=0, sticky="nswe")
        scrollbar = tk.Scrollbar(self, command=self.textbox.yview)
        self.textbox["yscrollcommand"] = scrollbar.set
        scrollbar.configure(command=self.textbox.yview)

        self.textbox.grid(row=1, column=0, sticky="we")
        scrollbar.grid(row=1, column=1, sticky="nswe")
        close.grid(row=0, column=0, sticky="nse", padx=5, pady=5)
        confirm.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)
        frame.grid(row=2, column=0, sticky="nswe", columnspan=2)
        
        self.write(str(Order()))
    
    def write(self, value):
        self.textbox["state"] = tk.NORMAL
        self.textbox.insert(tk.END, value)
        self.textbox["state"] = tk.DISABLED
    
    @classmethod
    def confirmation(cls, parent, payment_method, cash, change, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)

        cls.__init__(cls.instance, parent, payment_method, cash, change, **kwargs)
        return cls.instance


def labelentry(parent, text, variable, font=("Courier", 16), state=tk.DISABLED, **kwargs):
    frame = tk.Frame(parent, **kwargs)
    label = tk.Label(frame, font=font, text=text)
    entry = tk.Entry(frame, 
                font=font,
                textvariable=variable,
                state=state,
                width=10,
                disabledbackground="white",
                disabledforeground="black")

    label.grid(row=0, column=0, sticky="nse")
    entry.grid(row=0, column=1, sticky="nsw")
    return frame



class CheckoutFrame(OrdersFrame, metaclass=MenuWidget, device="POS"):
    font=("Courier", 16)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, widgettype=CheckoutTicketFrame)
        self.num_payment_types = len(CheckoutFrame.payment_types)
        self._ticket = tk.StringVar(self)
        self._ticket.set("000")
        labelentry(self.interior, "Ticket     ", self._ticket, 
                relief=tk.RIDGE, bd=2).grid(
                        row=0,
                        column=0,
                        padx=10,
                        pady=10,
                        columnspan=2,
                        sticky="nswe")

        calculator = ChangeCalculator(
                self.interior,
                bd=2,
                relief=tk.RIDGE)
        
        calculator.grid(row=1, column=0,
                rowspan=2,
                columnspan=2,
                sticky="nswe",
                pady=10,
                padx=10)

        calculator.update()
    
        self.buttons = [
                LabelButton(self.interior, payment_type, font=self.font) 
                for payment_type in self.payment_types] # pylint:disable=E1101
        
        for i, button in enumerate(self.buttons):
            button.grid(row=i + 3, column=0, columnspan=2, sticky="nswe", padx=10, pady=2)        
            button.command = partial(ConfirmationWindow,
                    self.interior,
                    button["text"],
                    calculator.cash,
                    calculator.change)
        self.update_ticket_no()

    @property
    def ticket(self) -> int:
        return int(self._ticket.get())
    
    @ticket.setter
    def ticket(self, value:int):
        assert isinstance(value, int)
        self._ticket.set("{:03d}".format(value))

    def ticket_number(self, **kwargs):
        frame = tk.Frame(self.interior, **kwargs)
        label = tk.Label(frame, text="Next Ticket", font=self.font)
        entry = tk.Entry(frame, 
                textvariable=self._ticket,
                font=self.font,
                width=5,
                state=tk.DISABLED,
                disabledforeground="black",
                disabledbackground="white")
        label.grid(row=0, column=0, sticky="nswe")
        entry.grid(row=0, column=1, sticky="nswe")
        return frame


    @update
    def update_ticket_no(self):
        AsyncTk().forward("get_ticket_no", self._ticket)

    @update
    def update_order_list(self):
        

        if not Order():
            for button in self.buttons:
                button.deactivate()
        else:
            for button in self.buttons:
                button.activate()
        
        grid_offset = self.num_payment_types
        order_size = len(Order())
        self.tickets.realloc(order_size)
        cache_size = len(self.tickets)

        for i, ticket in enumerate(Order()):
            self.tickets[i]._update(ticket)
            self.tickets[i].grid(row=i + grid_offset + 3,
                    column=0,
                    padx=10,
                    pady=5,
                    sticky="nswe")
       
        for widget in self.tickets[order_size:cache_size]:
            widget.grid_remove()