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
from lib import Ticket
from .order import Order
from .order_display import ItemLabel
from .order_display import TicketFrame
from .order_display import OrdersFrame
import lib
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

    def __init__(self, master, text, **kwargs):
        super().__init__(master,
                text,
                font=self.font,
                **kwargs)

    def _update(self, ticket):
        # during initiation, ticket.parameters is given a boolean type.
        register = ticket.parameters.get("register", False)
        
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
        self.checkbutton = RegisterButton(self, "register", width=9)
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
            widget._update(lib.NULL_TICKET_ITEM)


class ChangeCalculator(tk.Frame, metaclass=WidgetType, device="POS"):
    font = ("Courier", 16)
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.cash_given = tk.StringVar(self)
        self.change_due = tk.StringVar(self)
        self.cash_given.set("0.00")
        cash_given_frame = tk.Frame(self)
        label = tk.Label(self, text="Cash Given ", font=self.font)
        self.price_input = lib.PriceInput(self, textvariable=self.cash_given, font=self.font, width=10)
        label.grid(row=0, column=0, sticky="nswe")
        self.price_input.grid(row=0, column=1, sticky="nswe")
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
    
    def set_keypress_bind(self, notebook, tabname, on_enter=lambda:None):
        def input_condition():
            return notebook.current() == tabname
        return self.price_input.set_keypress_bind(lib.AsyncTk(),
                condition=input_condition,
                on_enter=on_enter)

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

    instance = None

    def __init__(self, parent, payment_type, cash, change, var, **kwargs):
        super().__init__(parent, **kwargs)
        self.title("Confirm Order")
        self.grid_columnconfigure(0, weight=1)
        self.cash = cash
        self.var = var
        self.change = change
        self.payment_type = payment_type
        self.textbox = tk.Text(self, font=self.font, 
                width=32,
                height=10,
                bg="grey26",
                fg="white")
        self.textbox.insert('0.0',str(Order()))
        self.textbox.configure(
                state=tk.DISABLED)
        self.name = lib.LabeledEntry(self,
                text="Name:",
                font=("Courier", 14))
        self.name.configure_entry(
                width=25)
        if self.payment_type not in lib.CONST_PAYMENT_TYPES:
            self.name.set(self.payment_type)

        frame = tk.Frame(self,
                relief=tk.RIDGE,
                bd=2)
        self.deliver = lib.ToggleSwitch(frame, "Deliver",
                width=8,
                font=("Courier", 12, "bold"))
        close = tk.Button(frame,
                text="Close",
                bg="red",
                width=8,
                command=self.destroy,
                font=("Courier", 12, "bold"))
        confirm = tk.Button(frame,
                text="Confirm",
                bg="green",
                width=8,
                command=self.on_confirm,
                font=("Courier", 12, "bold"))
        label = tk.Label(self,
                text=payment_type,
                font=self.font)
        label.grid(row=0,
                column=0,
                sticky="nswe")
        self.name.grid(
                row=1,
                column=0,
                sticky="nswe",
                padx=2)
        scrollbar = tk.Scrollbar(self,
                command=self.textbox.yview)
    
        self.textbox["yscrollcommand"] = scrollbar.set
        scrollbar.configure(
                command=self.textbox.yview)
        self.textbox.grid(
                row=2,
                column=0,
                sticky="nswe")
        scrollbar.grid(
                row=2,
                column=1,
                sticky="nswe")
        self.deliver.pack(
                side=tk.LEFT,
                ipady=8,
                padx=2,
                pady=2)
        confirm.pack(
                side=tk.RIGHT,
                ipady=4,
                padx=2,
                pady=2)
        close.pack(
                side=tk.RIGHT,
                ipady=4,
                padx=2,
                pady=2)
        frame.grid(
                row=3,
                column=0,
                sticky="nwse",
                columnspan=2)
        self.bind("<KP_Enter>", self.on_confirm)
        self.name.entry.focus_set()
    
    def on_confirm(self, *args):
            AsyncTk().forward("new_order", self.payment_type,
                    self.cash, self.change,
                    self.name.get(), self.deliver.state)
            self.var.set("0.00") # pointless since calculator self updates. remove later
            self.destroy()
        
    # i don't think anything calls this method
    @classmethod
    def confirmation(cls, parent, payment_method, cash, change, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)

        cls.__init__(cls.instance, parent, payment_method, cash, change, **kwargs)
        return cls.instance


class PaymentTypes(tk.Frame, metaclass=lib.ReinstanceType, device="POS"):
    font=("Courier", 18)
    button_args = ()

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.buttons = [
                LabelButton(self, payment_type, font=self.font, width=15) 
                for payment_type in type(self).payment_types] # pylint:disable=E1101
        
        self.cash_button = None
        rowcount = 3
        columncount = 0
        for i, button in enumerate(self.buttons):
            if i < 3:
                button.grid(row=i, column=0, columnspan=2, sticky="nswe", padx=10, pady=2)        
            else:
                button.configure(font=(self.font[0], self.font[1] + 2))
                if columncount == 2:
                    columncount = 0
                    rowcount += 1
                button.grid(row=rowcount, column=columncount, sticky="nswe", padx=10, pady=2)
                columncount += 1
                        
            if button["text"] == "Cash":
                self.cash_button = button
        assert self.cash_button is not None
        self.ctor_args = None

    def ctor(self):
        self.set_button_command(*type(self).button_args)
    
    def dtor(self):
        ...
    
    def set_button_command(self, cash, change, cash_given):
        type(self).button_args = cash, change, cash_given
        for button in self.buttons:
            button.command = partial(ConfirmationWindow,
                        self.master,
                        button["text"],
                        cash,
                        change,
                        cash_given)


class CheckoutFrame(OrdersFrame, metaclass=lib.MenuWidget, device="POS"):
    font=("Courier", 16)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, widgettype=CheckoutTicketFrame)
        self.interior.grid_columnconfigure(0, weight=1)
        self.interior.grid_columnconfigure(1, weight=1)

        self.num_payment_types = len(CheckoutFrame.payment_types)
        self._ticket = tk.StringVar(self)
        self._ticket.set("000")       
       
        self.ticket_no = lib.LabeledEntry(self.interior,
                text="Ticket     ", 
                textvariable=self._ticket,
                font=self.font,
                bd=2,
                relief=tk.RIDGE)
        self.ticket_no.configure_entry(
                width=10,
                state=tk.DISABLED,
                disabledbackground="white",
                disabledforeground="black")
        self.ticket_no.grid(
                row=0,
                column=0,
                sticky="nswe",
                columnspan=2,
                pady=2,
                padx=10)
        self.calculator = ChangeCalculator(
                self.interior,
                bd=2,
                relief=tk.RIDGE)
        
        self.set_keypress_bind = self.calculator.set_keypress_bind
        
        self.calculator.grid(row=2, column=0,
                rowspan=2,
                columnspan=2,
                sticky="nswe",
                pady=10,
                padx=10)
        
        self.payment_frame = PaymentTypes(self.interior)
        self.payment_frame.grid(row=4, column=0, columnspan=2, sticky="nswe")
        self.payment_frame.set_button_command(
                    self.calculator.cash,
                    self.calculator.change,
                    self.calculator.cash_given)
        
        self.update_ticket_no()
        self.calculator.update()

    def on_enter(self):
        if self.calculator.change_due.get() != "- - -":
            ConfirmationWindow(
                self.interior,
                "Cash",
                self.calculator.cash,
                self.calculator.change,
                self.calculator.cash_given)
    
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
            for button in self.payment_frame.buttons:
                button.deactivate()
        else:
            for button in self.payment_frame.buttons:
                button.activate()
        
        grid_offset = self.num_payment_types
        order_size = len(Order())
        self.tickets.realloc(order_size)
        cache_size = len(self.tickets)

        for i, ticket in enumerate(Order()):
            self.tickets[i]._update(ticket)
            self.tickets[i].grid(row=i + grid_offset + 3,
                    column=0,
                    columnspan=2,
                    padx=10,
                    pady=5,
                    sticky="nswe")
        
        for widget in self.tickets[order_size:cache_size]:
            widget.grid_remove()
        
        if self.calculator.change_due.get() == "- - -":
            self.payment_frame.cash_button.deactivate()
        else:
            self.payment_frame.cash_button.activate()