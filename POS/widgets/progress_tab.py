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


def alert(message):
    logging.getLogger("main.POS.gui.stdout").info(f"ALERT - {message}")

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
        

class ItemEditorType(MenuWidget):

    null_item = MutableTicket(("", "", 0, {}, [], {}))

    def item_names(self, category):
        try:
            return list(self.menu_items[category].keys())
        except KeyError:
            return list()
    
    def item_lookup(self, category, name):
        item = self.menu_items[category][name]
        return item["Price"], item["Options"]

    def __call__(self, parent, **kwargs):
        result = (super().__call__(parent, **kwargs),
                super().__call__(parent, **kwargs),
                super().__call__(parent, **kwargs))
        return result


class ItemEditor(metaclass=ItemEditorType, device="POS"):
    font = ("Courier", 14)
    style = None

    def __new__(cls, parent, **kwargs):
        if cls.style is None:
            cls.style = ttk.Style(parent)
            cls.style.configure("ItemEditor.TCombobox", 
                    font=cls.font)
            cls.style.map("ItemEditor.TCombobox",
                    fieldbackground=[("readonly", "white")],
                    selectbackground=[("readonly", "white")],
                    selectforeground=[("readonly","black")])
        return super().__new__(cls)
        
    def __init__(self, parent, **kwargs):
        self.removed = True
        self._ticket = None
        self.category = None
        self.item_selector = ttk.Combobox(parent,
                state="readonly",
                style="ItemEditor.TCombobox",
                font=self.font,
                width=type(self).longest_item,
                postcommand=self.send_alert)
        
        self.edit_options = LabelButton(parent, "Options",
                width=7,
                font=self.font,
                command=self._options_callback(parent))
        
        self.remove_item = LabelButton(parent, "Remove",
                width=7,
                font=self.font,
                bg="red",
                command=self._remove_callback)

        self.add_item = LabelButton(parent, "",
                width=7,
                font=self.font,
                command=self._add_callback)

    def grid(self, row=None, column=None, isaddon=True):
        if isaddon:
            self.item_selector.grid(row=row, column=column +1, sticky="nswe", padx=2, pady=1)
            self.add_item.grid(row=row, column=column +1, sticky="nswe", padx=2, pady=1)
        else:
            self.item_selector.grid(row=row, column=column, columnspan=2, sticky="nswe", padx=2, pady=1)
            self.add_item.grid(row=row, column=column, columnspan=2, sticky="nswe", padx=2, pady=1)
        self.edit_options.grid(row=row, column=column +3, sticky="nswe", padx=2, pady=1)
        self.remove_item.grid(row=row, column=column +4, sticky="nswe", padx=2, pady=1)

    def send_alert(self):
        if self.ticket.parameters.get("register", False):
            alert(f"'{self.ticket.name}' may have been completed")

    @property
    def ticket(self):
        return self._ticket
    
    @ticket.setter
    def ticket(self, value):
        self.category = value.category
        self.item_selector["values"] = type(self).item_names(value.category)
        self.item_selector.set(value.name)
        self.add_item["text"] = value.category
        
        if value.name:
            self._add_callback()
        else:
            self._remove_callback()
        self._ticket = value

    def get(self):
        if self.removed or self.ticket is None:
            return type(self).null_item
        
        item_name = self.item_selector.get()
        if item_name:
            self.ticket.name = item_name
            self.ticket.price, self.ticket.options = \
                     type(self).item_lookup(self._ticket.category, item_name)
        else:
            self.ticket.price = 0
            self.ticket.selected_options.clear()
            self.ticket.parameters.clear()
        return self.ticket

    def _remove_callback(self, *args):
        self.removed = True
        if self.ticket is not None:
            self.send_alert()
        self.item_selector.lower()
        self.edit_options.grid_remove()
        self.remove_item.grid_remove()
        self.add_item.lift()
    
    def _add_callback(self, *args):
        self.removed = False
        self.item_selector.lift()
        self.edit_options.grid()
        self.remove_item.grid()
        self.add_item.lower()

    def _options_callback(self, parent):
        def inner(*args):
            EditOptions(parent, self.get())
        return inner
    
    def destroy(self, *args):
        self.item_selector.destroy()
        self.edit_options.destroy()
        self.remove_item.destroy()
        self.add_item.destroy()
    

class TicketEditor(tk.Frame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        ttk.Separator(self).grid(row=0, column=0, columnspan=5, sticky="nswe", padx=2, pady=5)
        self.item_editors = item, addon1, addon2 = ItemEditor(self)
        
        # prevent frame from 
        tk.Label(self, width=2, font=ItemEditor.font).grid(row=2, column=0, sticky="nswe", padx=2)
        item.grid(row=1, column=0, isaddon=False)
        addon1.grid(row=2, column=0)
        addon2.grid(row=3, column=0)
        self.isgridded = True
    
    def total(self):    
        return sum(item.get().total for item in self.item_editors)
    
    def grid(self, **kwargs):
        super().grid(**kwargs)
        self.isgridded = True
    
    def grid_remove(self):
        super().grid_remove()
        self.isgridded = False

    @property
    def removed(self):
        return all(item.removed for item in self.item_editors)

    def set(self, *items):
        for i, editor in enumerate(self.item_editors):
            editor.ticket = items[i]
            
    def get(self):
        ticket = MutableTicket(self.item_editors[0].get())
        ticket.data.extend((self.item_editors[1].get(), self.item_editors[2].get()))
        return ticket


class EditorCalculator(ChangeCalculator, device="POS"):
    font = ("Courier", 14)

    def update(self, difference):
        change = difference - self.cash
        if change > 0 or difference == 0:
            self.change_due.set("- - -")
        else:
            self.change_due.set("{:.2f}".format(change / 100))


class TicketEditorFrame(tk.Frame):
            
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs) 
        self.widgets = WidgetCache(TicketEditor, self, initial_size=4)
        
        tk.Label(self, width=3, font=ItemEditor.font).grid(row=0, column=0, sticky="nswe", padx=2, ipadx=2)
        self.calculator_frame = tk.Frame(self, bd=2, relief=tk.RIDGE)
        self.calculator = EditorCalculator(self.calculator_frame)
        self._difference = tk.StringVar(self)

        self.difference_label = tk.Label(self.calculator_frame, text="Difference ", font=ItemEditor.font)
        self.difference_entry = tk.Entry(self.calculator_frame, 
                textvariable=self._difference,
                font=ItemEditor.font,
                state=tk.DISABLED,
                disabledforeground="black",
                disabledbackground="white",
                width=10)
        
        self.difference_label.grid(row=0, column=0, sticky="w")
        self.difference_entry.grid(row=0, column=1, sticky="w")
        self.calculator.grid(row=1, column=0, sticky="w", columnspan=2)

        self.calculator_frame.grid(row=0, column=1, sticky="nswe", columnspan=2, pady=2, padx=2)
        self.ticket_no = None
        self.is_gridded = False
        self.original_total = None

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

    def set(self, ticket_no, index):
        self.ticket_no = int(ticket_no)
        self.original_total, order_list = AsyncTk().forward(
                "get_order_info", self.ticket_no, "total", "items")
        self.widgets.realloc(len(order_list))

        for i, ticket in enumerate(order_list):
            item, addon1, addon2 = (MutableTicket(ticket),
                    MutableTicket(ticket[6]),
                    MutableTicket(ticket[7]))

            # combobox needs to know what items to show by looking up
            # the item's category
            self.widgets[i].set(*self.set_category(item, addon1, addon2))
            self.widgets[i].grid(row=i + 1, column=1, columnspan=4, sticky="nswe")
    
        # remove excess cached widgets
        for ticket in self.widgets[len(order_list):len(self.widgets)]: 
            ticket.grid_remove()
        self.grid(row=index, column=0, columnspan=5, sticky="nswe", pady=2)

    @staticmethod
    def set_category(item, addon1, addon2):
        sides = "Sides"
        drinks = "Drinks"
        if item.category in ItemEditor.two_sides:
            addon1.category = sides
            addon2.category = sides
        elif item.category in ItemEditor.no_addons:
            addon1.category = ""
            addon2.category = ""
        else:
            addon1.category = sides
            addon2.category = drinks
        return item, addon1, addon2
    
    def grid(self, **kwargs):
        self.is_gridded = True
        super().grid(**kwargs)

    def grid_remove(self):
        self.is_gridded = False
        super().grid_remove()

    def create_order(self):
        return [widget.get() for widget in self.widgets if not widget.removed]
      
    @update
    def update(self):
        if not self.is_gridded:
            return
        self.difference = sum(widget.total() for widget in self.widgets) - self.original_total
        self.calculator.update(self.difference)


class ConfirmationFrame(tk.Frame):
    
    def __init__(self, parent, first="Confirm", font=None, **kwargs):
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
        self._status.set(value)

class OrderProgress(tk.Frame, metaclass=MenuWidget, device="POS"):
    font=("Courier", 14)
    editor = None
    confirm_modify = None

    def __new__(cls, parent, **kwargs):
        if cls.editor is None:
            cls.editor = TicketEditorFrame(parent)
            cls.editor.update()
            cls.confirm_modify = ConfirmationFrame(parent, first="Return", font=cls.font)
        return super().__new__(cls)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(2, weight=1)
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
    
    def _update(self, ticket_no):
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
        items, = AsyncTk().forward("get_order_info", int(self.ticket_no["text"]), "items")
        names = []
        for ticket in items:
            for item in (ticket[:6], ticket[6], ticket[7]):
                if item[5].get("register", False):
                    names.append(f"'{item[1]}'")
        alert(f"{', '.join(names)} may have been completed.")
        self.confirm_cancel.lift()

    def on_modify(self, *args):
        self.confirm_modify.grid(row=1,
                column=3,
                columnspan=2,
                sticky="nswe",
                in_=self)

        self.confirm_modify.lift()
        self.editor.set(str(int(self.ticket_no["text"])), self.index + 1)
    
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
        for i, ticket in enumerate(order_queue):
            self.widget_cache[i]._update(ticket)
            self.widget_cache[i].grid(row=(cache_size - i) * 2, column=0, columnspan=5, sticky="we", padx=5)
            self.widget_cache[i].index = (cache_size - i) * 2
        
        # remove excess cached widgets
        for widget in self.widget_cache[queue_size:cache_size]:
            widget.grid_remove()
