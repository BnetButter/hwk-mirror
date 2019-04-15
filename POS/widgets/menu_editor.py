from lib import MenuType
from lib import MENUDATA
from lib import MenuItem
from tkinter import ttk
import lib
import decimal
import logging
import sys
import json
import tkinter as tk
import functools
from copy import deepcopy

class EditorDelegate(metaclass=lib.SingletonType):

    def __init__(self):
        self.menu = deepcopy(MenuType.menu_items)
        self.config = deepcopy(MenuType.menu_config)
        
    def remove_item(self, category, name):
        self.menu[category].pop(name)
        return f"Removed '{name}' from '{category}'"
        
    def add_item(self, category, name, price, options):
        if category and name:
            self.menu[category][name] = {
                "Price":price,
                "Options":options}

            return f"Added '{name}' to '{category}'"
        return ""

    def config_add(self, config, category):
        category_list = self.config[config]
        if category not in category_list:
            category_list.append(category)
            return f"'{config}' applied to '{category}'"
        return ""
    
    def config_remove(self, config, category):
        category_list = self.config[config]
        if category in category_list:
            category_list.remove(category)
            return f"'{config}' does not apply to '{category}'"
        return ""
    
    def edit_item(self, category, name, price, options):
        if category in self.menu \
                and name in self.menu[category]:
          
            original_price = self.menu[category][name]["Price"]
            original_options = self.menu[category][name]["Options"]
            
        
            changes_message = list()        
            if price != original_price:
                changes_message.append("    price: {:.2f} -> {:.2f}".format(original_price/100, price/100))

            if options != original_options:
                added = [option for option in options if option not in original_options]
                removed = [option for option in original_options if option not in options]

                for i, option in enumerate(added):
                    added[i] =    "     added {}: {:.2f}".format(option, options[option])
                for i, option in enumerate(removed):
                    removed[i] = f"     removed option: {option}"

                changed_prices = [(option, original_options[option], options[option]) 
                        for option in options 
                            if option in original_options
                                and  options[option] != original_options[option]]
                
                for i, option in enumerate(changed_prices):
                    option, old_price, new_price = option
                    changed_prices[i] = "    edited {}: {:.2f} -> {:.2f}".format(option, old_price/100, new_price/100)
                
                if added:
                    changes_message.append("\n".join(added))
                if removed:
                    changes_message.append("\n".join(removed))
                if changed_prices:
                    changes_message.append("\n".join(changed_prices))

                self.menu[category][name]["Price"] = price  
                self.menu[category][name]["Options"].clear()
                self.menu[category][name]["Options"].update(options)
            
            if changes_message:
                print(changes_message)
                return f"Changed '{name}' in '{category}'" + "\n" + "\n".join(changes_message)
            return ""
        return self.add_item(category, name, price, options)

    def apply(self):
        MenuType.menu_items.clear()
        MenuType.menu_config.clear()
        MenuType.menu_items.update(self.menu)
        MenuType.menu_config.update(self.config)
        return {"menu":self.menu, "config":self.config}
    
    def reset(self):
        self.__init__()

class PriceEntry(tk.Frame):
    keyboard = None

    def __init__(self, parent, font=("Courier", 14), **kwargs):
        super().__init__(parent, **kwargs)
        self._item = tk.StringVar(self)
        self._price = tk.StringVar(self)
        self.item_entry = tk.Entry(self, textvariable=self._item, font=font)
        self.price_entry = tk.Entry(self, textvariable=self._price, width=5, font=font)
        self.item_entry.grid(row=0, column=0, sticky="nswe", padx=2)
        self.price_entry.grid(row=0, column=1, sticky="nswe", padx=2)
        self.item_entry.bind("<FocusIn>", self.acquire(self.item_entry))
        self.price_entry.bind("<FocusIn>", self.acquire(self.price_entry))

    def acquire(self, entry):
        def _inner(event):
            self.keyboard.target = entry
        return functools.partial(_inner)

    @property
    def item(self):
        return self._item.get()
    
    @item.setter
    def item(self, value):
        self._item.set(value)
    
    @property
    def price(self):
        price = self._price.get().strip()
        if not price:
            return 0

        return int(decimal.Decimal(price).quantize(decimal.Decimal('.01'), 
                rounding=decimal.ROUND_HALF_UP) * 100)
    
    @price.setter
    def price(self, value):
        if isinstance(value, str) and not value:
            return self._price.set(value)
        self._price.set("{:.2f}".format(value/100))


class ItemOptionsEditor(PriceEntry, metaclass=lib.MenuWidget, device="POS"):
    font=("Courier", 14)

    def __init__(self, parent, option="", price=0, **kwargs):
        super().__init__(parent, **kwargs)
        self.item = option
        self.price = price
        self.item_entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=2)
        self.price_entry.grid(row=0, column=2, sticky="nswe", padx=2)
        self.removed = False
        self.remove_bt = lib.LabelButton(self, "Remove", 
                width=7,
                font=self.font,
                command=self.destroy)
        self.remove_bt.grid(row=0, column=3, sticky="nswe", padx=2)

    def destroy(self, *args):
        self.removed = True
        super().destroy()
    

class MenuItemEditor(PriceEntry, metaclass=lib.MenuWidget, device="POS"):
    font=("Courier", 14)
    
    def __init__(self, parent, menu_item=None):
        super().__init__(parent)        
        if menu_item is None:
            menu_item = lib.MenuItem("", "", 0, {})

        self.removed = True
        self.category = menu_item.category
        self.item = menu_item.name
        self.price = menu_item.price

        self.item_entry["font"] = self.font
        self.price_entry["font"] = self.font
        self.options_bt = lib.LabelButton(self, text="Options", width=7, font=self.font)
        self.remove_bt = lib.LabelButton(self, text="Remove", width=7, font=self.font, command=self.grid_remove)
        self.options_bt.grid(row=0, column=2, sticky="nswe", padx=2)
        self.remove_bt.grid(row=0, column=3, sticky="nswe", padx=2)



    def grid(self, **kwargs):
        self.removed = False
        super().grid(**kwargs)

    def grid_remove(self):
        self.removed = True
        super().grid_remove()

    def get(self):
        if self.removed:
            message = EditorDelegate().remove_item(self.category, self.item)
            logging.getLogger("main.POS.gui.stdout").info(message)
            return ("", "", 0)
        else:
            return self.category, self.item, self.price
            

class OptionEditorFrame(tk.Frame):

    def __init__(self, parent, options, **kwargs):
        super().__init__(parent, **kwargs)
        self.options = options
        self.add_button = lib.LabelButton(self, "add",
                width=5,
                font=ItemOptionsEditor.font,
                command=self._add_callback)
        
        self.close_button = lib.LabelButton(self, "close",
                width=5,
                font=ItemOptionsEditor.font,
                command=self._close_callback)

        self.widgets = [ItemOptionsEditor(self,
                option=option,
                price=self.options[option])
                     for option in self.options]
        self.add_button.grid(row=0, column=0, sticky="nswe", padx=2, pady=2)
        self.close_button.grid(row=0, column=1, sticky="nswe", padx=2, pady=2)

        for i, widget in enumerate(self.widgets):
            widget.grid(row=i +1, column=0, columnspan=4, sticky="nswe")
        
    
    def _add_callback(self, *args):
        widget = ItemOptionsEditor(self)
        widget.grid(column=0, columnspan=4, sticky="nswe")
        self.widgets.append(widget)
    
    def _close_callback(self, *args):
        for widget in self.widgets:
            if widget.item.strip():
                self.options[widget.item] = widget.price
        self.grid_remove()
    
    def get(self):
        return {
            widget.item:widget.price
            for widget in self.widgets
                if widget.item and not widget.removed
        }
        

class ItemEditor(tk.Frame):

    def __init__(self, parent, menu_item, **kwargs):
        super().__init__(parent, **kwargs)
        self.item_editor = MenuItemEditor(self, menu_item)
        self.option_editor = OptionEditorFrame(self, menu_item.options)
        self.item_editor.grid(row=0, column=0, columnspan=4, sticky="nswe")
        self.item_editor.options_bt.command = self._option_callback
    
    @property
    def removed(self):
        return self.item_editor.removed
    
    def _option_callback(self, *args):
        self.option_editor.grid(row=1, column=1, columnspan=3, sticky="nswe")

    def get(self):
        category, name, price = self.item_editor.get()
        return category, name, price, self.option_editor.get()

class EditorCategoryFrame(lib.ScrollFrame, metaclass=MenuType):

    def __init__(self, parent, category, **kwargs):
        super().__init__(parent, **kwargs)
        self.widgets = []
        self.category = category
        for i, menu_item in enumerate(type(self).category(category)):
            editor = ItemEditor(self.interior, menu_item)
            editor.grid_rowconfigure(i, weight=1)
            editor.grid(row=i, column=0, columnspan=4, sticky="nswe")
            
            self.widgets.append(editor)
    
    def is_empty(self):
        return not len(tuple(widget for widget in self.widgets if not widget.removed))

    def add_item(self, category, name, price):
        item_widget = ItemEditor(self.interior, MenuItem(category, name, price, {}))
        item_widget.grid(row=len(self.widgets), column=0, columnspan=4, sticky="nswe")
        self.widgets.append(item_widget)
        

class MenuEditorTabs(lib.TabbedFrame, metaclass=lib.MenuWidget, device="POS"):
    tabfont = ("Courier", 14)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.style.configure("MenuEditor.TNotebook.Tab",
            font=self.tabfont,
            padding=5)
        self._notebook["style"] = "MenuEditor.TNotebook"
        for category in type(self).categories:
            self[category] = EditorCategoryFrame(self, category)
    
    def apply(self):
        return "\n".join((EditorDelegate().edit_item(*item_editor.get())
            for editor in self.data.values()
                for item_editor in editor.widgets))


class ConfigFrame(tk.Frame, metaclass=MenuType):

    def __init__(self, parent, category, font=None, **kwargs):
        super().__init__(parent, **kwargs)
        original_config = type(self).category_configurations()
        self.category = category
        self.widgets = [lib.ToggleSwitch(self, conf, font=font) for conf in original_config]
        for i, widget in enumerate(self.widgets):
            widget.grid(row=i, column=0, sticky="nswe", pady=2, padx=2)
            widget.on_release()

        self.grid_columnconfigure(0, weight=1)
        
        self.config = {
            config: self.category in original_config[config]
            for config in original_config
        }

    def update(self, category):
        if category != self.category:
            return
        self.lift()
        for widget in self.widgets:
            config = widget["text"]
            state = self.config[config]
            if isinstance(state, bool):
                widget.state = self.config[config] = int(state)
            else:
                self.config[config] = widget.state
        
    def apply(self):
        messages = list()
        for conf in self.config:
            if self.config[conf]:
                message = EditorDelegate().config_add(conf, self.category)
            else:
                message = EditorDelegate().config_remove(conf, self.category)
            messages.append(message)
        return "\n".join((message for message in messages if message))


class ItemAdder(tk.Frame):

    def __init__(self, parent, keyboard, font=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.keyboard = keyboard
        self._category = tk.StringVar(self)
        self._has_focus = False
        self.cat_entry = tk.Entry(self, textvariable=self._category, font=font)
        self.entry = PriceEntry(self, font=font)
        self.add_item = lib.LabelButton(self, "Add", font=font)
        self.cat_entry.grid(row=0, column=0, sticky="nswe", padx=2, pady=2)
        self.entry.grid(row=0, column=1, sticky="nswe", padx=2, pady=2)
        self.add_item.grid(row=0, column=2, sticky="nswe", ipadx=2, pady=2)
        self.cat_entry.bind("<FocusIn>", self.acquire)
        self.cat_entry.bind("<FocusOut>", self.on_focus_out)
    
    def on_focus_out(self, event):
        self._has_focus = False

    def acquire(self, *args):
        self.keyboard.target = self.cat_entry
        self._has_focus = True
    
    def clear(self):
        self.entry.item = ""
        self.entry.price = ""
        self.focus_set()
        
    def get(self):
        return self.category, self.entry.item, self.entry.price
    
    @property
    def category(self):
        return self._category.get()

    @category.setter
    def category(self, value):
        if not self._has_focus:
            self._category.set(value)

class ButtonFrame(tk.Frame):

    def __init__(self, parent, font=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.apply = lib.LabelButton(self, "Apply", font=font, width=6)
        self.save = lib.LabelButton(self, "Save", font=font, width=6)
        self.reset = lib.LabelButton(self, "Reset", font=font, width=6,
                bg="yellow")
    
        self.apply.grid(row=0, column=0, sticky="nswe", pady=2, padx=2)
        self.save.grid(row=1, column=0, sticky="nswe", pady=2, padx=2)
        self.reset.grid(row=2, column=0, sticky="nswe", pady=2, padx=2)
        self.grid_columnconfigure(0, weight=1)