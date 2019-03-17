# OrderDisplay child widget.
# "CheckoutFrame" is the scrollable container class for change calculator,
#      buttons specifying payment method, and an overview of "Orders" tab.

from lib import ScrollFrame
from lib import Order
from lib import MenuWidget
from lib import WidgetType
from lib import Ticket
from lib import ToggleSwitch
from lib import LabelButton
from lib import AsyncWindow
from lib import update
from .order_display import ItemLabel
from .order_display import TicketFrame
from .order_display import OrdersFrame
from collections import UserDict
from functools import partial
import tkinter as tk
import asyncio
import decimal



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

    def _update(self, index):
        try:
            order = Order()[index]
        except IndexError:
            return self.reset()

        tickets = order, order.addon1, order.addon2
      
        for i, ticket in enumerate(tickets):
            self.widgets[i]._update(ticket)
            self._grid_widgets(i, ticket)
            self._grid_forget(i, ticket)

    def reset(self):
        for widget in self.widgets:
            widget._update(self.null_ticket)


class PaymentMethod(tk.Frame, UserDict): 
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = {}
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = tk.Frame(self)
        assert hasattr(value, "command")
        value.command = self.data[key].lift

    def _grid_interior(self):
        num_frames = len(self.data)
        for i, frame in enumerate(self.data.values()):
            frame.grid(row=i, column=0, rowspan=num_frames, columnspan=3, sticky="nswe")

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
        AsyncWindow.append(self._update)

    @property
    def cash(self):
        try:
            result = self.cash_given.get().strip()
            result = decimal.Decimal(result).quantize(decimal.Decimal('.01'))
            return result * 100
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
        
        label.grid(row=0, column=0, sticky="nse")
        entry.grid(row=0, column=1, sticky="nsw")
        return frame

    @update
    def _update(self):
        change = Order().total - self.cash
        if change > 0 or Order().total == 0:
            self.change_due.set("- - -")
        else:
            self.change_due.set("{:.2f}".format(change / 100))
            


class ConfirmationWindow(tk.Toplevel, metaclass=WidgetType, device="POS"):
    font=("Courier", 12)

    def __init__(self, parent, payment_type, **kwargs):
        super().__init__(parent, **kwargs)
        self.title("Confirm Ticket")
        label = tk.Label(self, text=payment_type, font=self.font)
        label.grid(row=0, column=0, sticky="nswe")
        scrollbar = tk.Scrollbar(self)
        self.command=lambda *args:None
        self.textbox = tk.Text(self, font=self.font, 
                yscrollcommand=scrollbar.set,
                state=tk.DISABLED,
                bg="grey26",
                fg="white")

        scrollbar.configure(command=self.textbox.yview)
        self.textbox.grid(row=1, column=0, sticky="nswe")
        scrollbar.grid(row=1, column=1, sticky="nswe")

        frame = tk.Frame(self, relief=tk.RIDGE, bd=2)

        close = tk.Button(frame, text="Close", bg="red", command=self.destroy)
        confirm = tk.Button(frame, text="Confirm", bg="green", command=self.command)
        close.grid(row=0, column=0, sticky="nse", padx=5, pady=5)
        confirm.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)
        frame.grid(row=2, column=0, sticky="nswe", columnspan=2)

        self.write(str(Order()))

    def write(self, value):
        self.textbox["state"] = tk.NORMAL
        self.textbox.insert(tk.END, value)
        self.textbox["state"] = tk.DISABLED
    
    @classmethod
    def confirmation(cls, parent, payment_method, **kwargs):
        result = object.__new__(cls)
        cls.__init__(result, parent, payment_method, **kwargs)
        return result

class CheckoutFrame(OrdersFrame, metaclass=MenuWidget, device="POS"):
    font=("Courier", 16)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._ticket = tk.StringVar(self)
        self.ticket_number(relief=tk.RIDGE, bd=2).grid(
                row=0,
                column=0,
                padx=10,
                pady=10,
                columnspan=2,
                sticky="nswe")

        calculator = ChangeCalculator(self.interior, bd=2, relief=tk.RIDGE)
        calculator.grid(row=1, column=0, rowspan=2, columnspan=2, sticky="nswe", pady=10, padx=10)
        self.buttons = [
                LabelButton(self.interior, payment_type, font=self.font) 
                    for payment_type in self.payment_types] # pylint:disable=E1101
        for i, button in enumerate(self.buttons):
            button.grid(row=i + 3, column=0, columnspan=2, sticky="nswe", padx=10, pady=2)
        
        for button in self.buttons:
            button.command = partial(ConfirmationWindow.confirmation, parent, button["text"])
    
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

    async def update_order_list(self):

        while True:
            grid_offset = len(CheckoutFrame.payment_types)
            num_tickets = len(Order())
            if len(self.tickets) < num_tickets:
                    self.tickets.append(CheckoutTicketFrame(self.interior, bd=2, relief=tk.RIDGE))
            for i, ticket in enumerate(self.tickets):  
                if i < num_tickets:
                    ticket._update(i)
                    ticket.grid(row=i + grid_offset + 3,
                            column=0,
                            padx=10,
                            pady=5,
                            sticky="nswe")
                else:
                    ticket.grid_forget()
            await asyncio.sleep(1/60)
    




