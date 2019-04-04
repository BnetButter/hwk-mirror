# progress tab shows the current status of a order and provides 
# an interface to modify or cancel a order

from lib import AsyncTk, update
from lib import Ticket
from lib import MenuWidget, WidgetType, MenuType
from lib import LabelButton
from lib import ScrollFrame
from lib import WidgetCache
from lib import TicketType
from lib import ToggleSwitch
from lib import TICKET_COMPLETE, TICKET_QUEUED
from lib import Ticket
from .order import Order
from .order_display import EditOptions
from .checkout_display import ChangeCalculator

from operator import itemgetter
from collections import UserList
from tkinter import ttk
import functools
import tkinter as tk
import asyncio
import decimal
import logging

# essentially the same as lib.Ticket
class MutableTicket(UserList, metaclass=TicketType):
    def __init__(self, ticket):
        self.data = list(ticket[:6])

    @property
    def total(self):
        result = self.price
        for option in \
                (opt for opt in self.selected_options
                if opt in self.options):
            result += self.options[option]
        return result

    def create_ticket(self, addon1, addon2):
        self.data.append(addon1)
        self.data.append(addon2)
        return self
        
class ConfirmationFrame(tk.Frame):
    
    def __init__(self, parent, first="Confirm", font=None, **kwargs):
        assert first == "Confirm" or first == "Return"
        super().__init__(parent, **kwargs)

        self.confirm_bt = LabelButton(self, "Confirm", width=7, font=font, bg="green")
        self.return_bt = LabelButton(self, "Return", width=7, font=font)
        
        confirm_grid_info = {"row":0, "column":1,  "sticky":"nswe", "padx":2}
        return_grid_info = {"row":0, "column": 1,  "sticky":"nswe", "padx":2}

        if first == "Confirm":
            confirm_grid_info["column"] = 0
        else:
            return_grid_info["column"] = 0
        
        self.confirm_bt.grid(**confirm_grid_info)
        self.return_bt.grid(**return_grid_info)

    def set_confirm(self, command):
        self.confirm_bt.command = command
        
    def set_return(self, command):
        self.return_bt.command = command
    
# ttk has a Progressbar widget but can't easily control its height and width
class ProgressBar(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._status = tk.IntVar(self)
        self._bar = ttk.Progressbar(parent, variable=self._status, **kwargs)
        
    def grid(self, cnf={}, **kwargs):
        super().grid(cnf, **kwargs)
        self._bar.grid(cnf, **kwargs)
        self._bar.lift()

    @property
    def status(self):
        return self._status.get()

    @status.setter
    def status(self, value):
        assert value <= 100 and value >=0
        self._status.set(value)

class CheckButton(tk.Checkbutton):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._complete = tk.IntVar(self)
        self["variable"] = self._complete
    
    def command(self, ticket):
        def _cmd(*args):
            ticket.parameters["status"] = self.complete == TICKET_COMPLETE
        self["command"] = _cmd

        
    def update(self, ticket):
        if ticket.name:
            self.complete = ticket.parameters.get("status") == TICKET_COMPLETE
        else:
            self.complete = 0
        
        if self.complete:
            self["state"] = tk.DISABLED
        else:
            self["state"] = tk.NORMAL
        

    

    @property
    def complete(self):
        return self._complete.get()

    @complete.setter
    def complete(self, value):
        self._complete.set(int(value))

class ComboBox(ttk.Combobox, metaclass=MenuType):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, state="readonly", **kwargs)
        self._ticket = None
        self.removed = False
        self.category = None
        self["postcommand"] = self.postcommand

    def postcommand(self, *args):
        if self._ticket.parameters.get("status") == TICKET_COMPLETE:
            self["values"] = []
            logging.getLogger("main.POS.gui.stdout").info(f"'{self._ticket.name}' cannot be changed.")

    
    def grid(self, **kwargs):
        super().grid(**kwargs)
        self.removed = False
    
    def grid_remove(self):
        super().grid_remove()
        self.removed = True
    
    @property
    def ticket(self):
        return self._ticket
    
    @ticket.setter
    def ticket(self, value):
        self._ticket = value
        self.set(value.name)
        self.category = value.category
        self["values"] = [
            item.name for item in ComboBox.category(value.category)
        ]

    def get(self):
        name = super().get()
        if not name or self.removed:
            self._ticket.name = ""
            self._ticket.price = 0
            self._ticket.options = {}
            return self._ticket
        
        menu_item = ComboBox.get_item(self.category, name)
        self._ticket.name = menu_item.name
        self._ticket.price = menu_item.price
        self._ticket.options = menu_item.options
        return self._ticket

    # for AsyncTk().update
    def total(self):
        price = 0
        name = super().get()
        if not name or self.removed:
            return price

        menu_item = ComboBox.get_item(self.category, name)
        price += menu_item.price

        for item in self._ticket.selected_options:
            if item in self._ticket.options:
                price += self._ticket.options[item]
        return price


class TicketEditor(tk.Frame, metaclass=MenuWidget, device="POS"):
    font = ("Courier", 14)
    style = None

    def __new__(cls, parent, **kwargs):
        if cls.style is None:
            cls.style = ttk.Style(parent)
            cls.style.configure("TicketEditor.TCombobox", 
                    font=cls.font,
                    width=cls.longest_item)
            cls.style.map("TicketEditor.TCombobox",
                    fieldbackground=[("readonly", "white")],
                    selectbackground=[("readonly", "white")],
                    selectforeground=[("readonly","black")])
    
        return super().__new__(cls)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.item_box = ComboBox(self, width=ComboBox.longest_item)
        self.addon1_box = ComboBox(self, width=ComboBox.longest_addon)
        self.addon2_box = ComboBox(self, width=ComboBox.longest_addon)
        self.item_box["style"] = "TicketEditor.TCombobox"
        self.addon1_box["style"] = "TicketEditor.TCombobox"
        self.addon2_box["style"] = "TicketEditor.TCombobox"

        self.item_box.configure(font=self.font)
        self.addon1_box.configure(font=self.font)
        self.addon2_box.configure(font=self.font)
        
        spacer0 = tk.Label(self, text="", width=3, font=self.font)
        spacer1 = tk.Label(self, text="", width=8, font=self.font)

        spacer3 = tk.Label(self, text="", width=7, font=self.font)
        spacer4 = tk.Label(self, text="", width=7, font=self.font)
        spacer3.grid(row=1, column=3, sticky="nswe", pady=2, padx=2)
        spacer4.grid(row=1, column=4, sticky="nswe", pady=2, padx=2)


        self.remove = [LabelButton(self, "Remove", font=self.font, width=7, bg="red") for i in range(3)]
        self.options = [LabelButton(self, "Options", font=self.font, width=7) for i in range(3)]
        self.add_addon = [LabelButton(self, "", font=self.font) for i in range(3)]
        self.mark_complete = [CheckButton(self) for i in range(3)]

        ttk.Separator(self).grid(row=0, column=1, columnspan=4, sticky="we", pady=2)

        spacer0.grid(row=1, column=0, sticky="nswe")
        spacer1.grid(row=2, column=0, columnspan=2, sticky="nswe")

        self.item_box.grid(row=1, column=1, columnspan=2, sticky="w", pady=2)
        self.addon1_box.grid(row=2, column=2, sticky="nswe", pady=2)
        self.addon2_box.grid(row=3, column=2, sticky="nswe", pady=2)

        for i, checkbutton in enumerate(self.mark_complete):
            checkbutton.grid(row=i + 1, column=0, sticky="nswe", padx=2, pady=2)

        for i, option_bt in enumerate(self.options):
            option_bt.grid(row=i + 1, column=3, sticky="nswe", padx=2, pady=2)
            
        for i, remove_bt in enumerate(self.remove):
            remove_bt.grid(row=i + 1, column=4, sticky="nswe", padx=2, pady=2)
        
        for i, add_addon in enumerate(self.add_addon[1:]):
            add_addon.grid(row=i + 2, column=2, sticky="nswe", padx=2, pady=2)
            add_addon.grid_remove()
        
        self.add_addon[0].grid(row=1,
                column=1,
                columnspan=2,
                sticky="nswe",
                pady=2,
                padx=2)
    
        self.add_addon[0].grid_remove()
        self.removed = True

    def get_total(self):
        if self.item_box.category in self.two_sides:
            addon1_total = 0
            addon2_total = 0
        else:
            addon1_total = self.addon1_box.total()
            addon2_total = self.addon2_box.total()
        
        return (self.item_box.total()
                + addon1_total
                + addon2_total)

    def grid(self, **kwargs):
        super().grid(**kwargs)
        self.removed = False    

    def grid_remove(self):
        super().grid_remove()
        self.removed = True

    def create_ticket(self):
        null_ticket = ("", "", 0, {}, [], {})
        if not self.addon1_box.get().name:
            addon1 = MutableTicket(null_ticket)
        else:
            addon1 = self.addon1_box.ticket

        if not self.addon2_box.get().name:
            addon2 = MutableTicket(null_ticket)
        else:
            addon2 = self.addon2_box.ticket
    
        return self.item_box.get().create_ticket(addon1, addon2)

    def _update(self, item, addon1, addon2):

        self.item_box.ticket = item
        self.addon1_box.ticket = addon1
        self.addon2_box.ticket = addon2


        comboboxes = (self.item_box, self.addon1_box, self.addon2_box)
        
        for i, combobox in enumerate(comboboxes):
            self.mark_complete[i].command(combobox.ticket)
            self.mark_complete[i].update(combobox.ticket)
            add_item =  functools.partial(self.on_addon_add,
                    combobox,
                    self.options[i],
                    self.remove[i],
                    self.add_addon[i],
                    self.mark_complete[i])
        
            remove_item = functools.partial(self.on_addon_remove, 
                    combobox,
                    self.options[i],
                    self.remove[i],
                    self.add_addon[i],
                    self.mark_complete[i])

            self.options[i].command = functools.partial(self.edit_options, 
                    combobox)

            self.add_addon[i].command = add_item
            self.remove[i].command = remove_item
            
            if combobox.ticket.name:
                add_item()
            else:
                remove_item()
            

    def edit_options(self, combobox):
        EditOptions(self, combobox.get())
    
    @staticmethod
    def on_addon_remove(combobox, option_button, remove_button, addon_add, checkbutton):
        status = combobox.ticket.parameters.get("status") == TICKET_COMPLETE
        if status:
            return logging.getLogger("main.POS.gui.stdout").info(
                        f"Cannot remove '{combobox._ticket.name}'")

        combobox.grid_remove()
        option_button.grid_remove()
        remove_button.grid_remove()
        checkbutton.grid_remove()
        addon_add["text"] = combobox.category
        addon_add.grid()
    
    @staticmethod
    def on_addon_add(combobox, option_button, remove_button, addon_add, checkbutton):
        combobox.grid()
        option_button.grid()
        remove_button.grid()
        
        if combobox.ticket.parameters.get("register", False):
            checkbutton.grid()
        else:
            checkbutton.grid_remove()
                
        addon_add.grid_remove()


class TicketEditorFrame(tk.Frame):

    class EditorCalculator(ChangeCalculator, device="POS"):
        font = ("Courier", 14)
        difference = 0
     
        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.difference = 0
            
  
        @update
        def update(self, difference):
            change = difference - self.cash
            if change > 0 or difference == 0:
                self.change_due.set("- - -")
            else:
                self.change_due.set("{:.2f}".format(change / 100))
            
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs) 
        self.widgets = WidgetCache(TicketEditor, self, initial_size=4)

        self.calculator_frame = tk.Frame(self, bd=2, relief=tk.RIDGE)
        self.calculator = self.EditorCalculator(self.calculator_frame)
        self._difference = tk.StringVar(self)


        self.difference_label = tk.Label(self.calculator_frame, text="Difference ", font=TicketEditor.font)
        self.difference_entry = tk.Entry(self.calculator_frame, 
                textvariable=self._difference,
                font=TicketEditor.font,
                state=tk.DISABLED,
                disabledforeground="black",
                disabledbackground="white",
                width=10)
        
        self.difference_label.grid(row=0, column=0, sticky="w")
        self.difference_entry.grid(row=0, column=1, sticky="w")
        self.calculator.grid(row=1, column=0, sticky="w", columnspan=2)


        self.calculator_frame.grid(row=0, column=1, sticky="nswe", pady=2, ipadx=2)
        self.ticket_no = None
        self.is_gridded = False
        self.original = None
        self.original_total = None
        self.calculator.update(self.difference)

    @property
    def difference(self):
        try:
            result = self._difference.get()
            result = decimal.Decimal(result).quantize(decimal.Decimal(".01"))
            return int(result * 100)
        except:
            return 0

    @difference.setter
    def difference(self, value):
        self._difference.set("{:.2f}".format(value / 100))
        self.calculator.difference = value

    # only called if 'modify' button is presed
    def _update(self, ticket_no, index):
        self.original = AsyncTk().forward("order_queue")
        # so we know whether or not to remove ticket_editor_frame
         # from grid if order is canceled
        self.ticket_no = int(ticket_no)

        self.original_total, = AsyncTk().forward(
                "get_order_info", self.ticket_no, "total")

        order = self.original[ticket_no]["items"]
        self.widgets.realloc(len(order))
        

        for i, ticket in enumerate(order):
            # we want to be able to change the ticket
            item, addon1, addon2 = (MutableTicket(ticket),
                    MutableTicket(ticket[6]),
                    MutableTicket(ticket[7]))

           

            # combobox needs to know what items to display by looking up
            # the item's category
            self.set_category(item, addon1, addon2)
            self.widgets[i].grid(row=i + 1, column=0, columnspan=4, sticky="nswe")
            self.widgets[i]._update(item, addon1, addon2)
            
        # remove excess cached widgets
        for ticket in self.widgets[len(order):len(self.widgets)]: 
            ticket.grid_remove()

        self.grid(row=index, column=0, columnspan=4, sticky="nswe", pady=2)

    @staticmethod
    def set_category(item, addon1, addon2):
        sides = "Sides"
        drinks = "Drinks"
        if item.category in ComboBox.two_sides:
            addon1.category = sides
            addon2.category = sides
        
        elif item.category in ComboBox.no_addons:
            addon1.category = ""
            addon2.category = ""

        else:
            addon1.category = sides
            addon2.category = drinks
    
    def grid(self, **kwargs):
        self.is_gridded = True
        super().grid(**kwargs)

    def grid_remove(self):
        self.is_gridded = False
        super().grid_remove()

    def create_order(self):
        return [widget.create_ticket() for widget in self.widgets if not widget.removed]

    @update
    def update_difference(self):
        if self.ticket_no is None \
                or not self.is_gridded:
            return

        new_total = sum(widget.get_total() for widget in self.widgets if not widget.removed)
        self.difference = new_total - self.original_total

class OrderProgress(tk.Frame, metaclass=MenuWidget, device="POS"):
    font=("Courier", 14)
    editor = None
    confirm_modify = None

    def __new__(cls, parent, **kwargs):
        if cls.editor is None:
            cls.editor = TicketEditorFrame(parent)
            cls.editor.update_difference()
    
        if cls.confirm_modify is None:
            cls.confirm_modify = ConfirmationFrame(parent, first="Return", font=cls.font)

        return super().__new__(cls)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self.original_order = None
        self.ticket_no = tk.Label(self, font=self.font, relief=tk.SUNKEN, bd=1, bg="white")
        self.index = None
        
        self.progress = ProgressBar(self)
        self.cancel_button = LabelButton(self, "Cancel", width=7, font=self.font, bg="red", command=self.on_cancel)
        self.modify_button = LabelButton(self, "Modify", width=7, font=self.font, command=self.on_modify)
        
        self.confirm_cancel = ConfirmationFrame(self, font=self.font)
        self.confirm_cancel.set_confirm(self.on_cancel_confirm)
        self.confirm_cancel.set_return(self.on_cancel_return)
        
        self.confirm_modify.set_confirm(self.on_modify_confirm)
        self.confirm_modify.set_return(self.on_modify_return)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
                row=0, column=0,
                columnspan=5,
                sticky="we",
                pady=2)
    
        self.ticket_no.grid(row=1, column=0,
                sticky="nswe",
                padx=2)
        
        self.progress.grid(row=1, column=1,
                sticky="nswe",
                columnspan=2,
                padx=2)
        
        self.modify_button.grid(row=1, column=3, 
                padx=2,
                sticky="nswe")
        
        self.cancel_button.grid(row=1, column=4,
                padx=2,
                sticky="nswe")
        
        self.confirm_cancel.grid(row=1, column=3,
                columnspan=2,
                sticky="nswe")
        
        self.modify_button.lift()
        self.cancel_button.lift()
    


    def _update(self, ticket_no, progress):
        ticket_no = int(ticket_no)
        self.ticket_no["text"] = "{:03d}".format(ticket_no)
        self.progress.status = AsyncTk().forward("get_order_status", ticket_no)
        if self.progress.status == 100:
            self.cancel_button.deactivate()
            self.modify_button.deactivate()
        else:
            self.cancel_button.activate()
            self.modify_button.activate()

    def on_cancel(self):
        self.confirm_cancel.lift()

    def on_modify(self, *args):
        self.confirm_modify.grid(row=1,
                column=3,
                columnspan=2,
                sticky="nswe",
                in_=self)
        self.confirm_modify.lift()

        self.editor._update(str(int(self.ticket_no["text"])), self.index + 1)
    
    def on_cancel_confirm(self):
        self.cancel_button.lift()
        self.modify_button.lift()
        
        ticket_no = int(self.ticket_no["text"])
        original, = AsyncTk().forward("get_order_info", ticket_no, "items")
        
        modified_order = []
        for ticket in original:
            items = ticket[:6], ticket[6], ticket[7]        
            for item in items:
                if item[5].get("status") == TICKET_COMPLETE:
                    _item = MutableTicket(item)
                    null_ticket = MutableTicket(("", "", 0, {}, [], {}))
                    _item.data.extend((null_ticket, null_ticket))
                    modified_order.append(_item)

        if modified_order:
            names = ", ".join(f"'{ticket.name}'" for ticket in modified_order)
            logging.getLogger("main.POS.gui.stdout").info(
                f"{names} cannot be removed. Modifying ticket instead..."
            )
            return AsyncTk().forward("modify_order", ticket_no, modified_order)

        AsyncTk().forward("cancel_order", ticket_no)

        if self.editor.ticket_no == ticket_no:
            self.editor.grid_forget()
            self.confirm_modify.grid_forget()
    
    def on_cancel_return(self):
        self.cancel_button.lift()
        self.modify_button.lift()
    
    def on_modify_confirm(self, *args):
        AsyncTk().forward("modify_order",
                self.editor.ticket_no,
                self.editor.create_order())
        self.editor.grid_remove()
        self.confirm_modify.grid_remove()

    def on_modify_return(self):
        self.editor.grid_remove()
        self.confirm_modify.grid_remove()
        self.modify_button.lift()
        self.cancel_button.lift()

class ProgressFrame(ScrollFrame):

    def __init__(self, parent, initial_size=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.interior.grid_columnconfigure(1, weight=1)
        self.widget_cache = WidgetCache(OrderProgress, self.interior, initial_size=initial_size)

    @update
    def update_order_status(self):
        order_queue = AsyncTk().forward("order_queue")
        if order_queue is None:
            return
    
        queue_size = len(order_queue)
        self.widget_cache.realloc(queue_size)
        cache_size = len(self.widget_cache)

        for i, ticket_num in enumerate(order_queue):
            self.widget_cache[i]._update(ticket_num, 50)
            self.widget_cache[i].grid(row=(cache_size - i) * 2, column=0, columnspan=4, sticky="we", padx=10)
            self.widget_cache[i].index = (cache_size - i) * 2

        # remove excess cached widgets
        for widget in self.widget_cache[queue_size:cache_size]:
            widget.grid_remove()