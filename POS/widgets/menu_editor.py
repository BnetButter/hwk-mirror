from lib import MenuType
from lib import MENUDATA
from lib import MenuItem
import logging as log
import sys
import json
import tkinter as tk

logger = log.getLogger(__name__)
logger.setLevel(log.DEBUG)

output = log.StreamHandler(stream=sys.stdout)
output.setFormatter(
        log.Formatter("%(name)s - %(levelname)s - %(funcName)s - %(message)s"))
logger.addHandler(output)


class MenuEditor(metaclass=MenuType):

    def __init__(self, filename, itemclass=None):
        if itemclass is None:
            itemclass = MenuItem
        self.ItemClass = itemclass

        self.filename = filename
        self.all = []
        for category in MenuEditor.categories:
            self.all.extend(MenuEditor.category(category))

    def add_item(self, category, name, price, options):
        if (category, name) not in self.all:
            self.all.append(self.ItemClass(
                    category, name, price, options))
        logger.info(f"Added: {self.ItemClass(category, name, price, options)}")

    def remove_item(self, category, name):
        if (category, name) in self.all:
            self.all.pop(self.all.index((category, name)))
        logger.info(f"Removed: {(category, name)}")

    def edit_item(self, category, name, price, options):
        item = self.ItemClass(category, name, price, options)
        previous = self.all.pop(self.all.index((category, name)))
        self.all.append(item)
        logger.info(f"{previous} -> {item}")

    def to_dict(self):
        result = {"menu":{}, "config":{}}
        for item in self.all:
            result["menu"][item.category] = dict()

        for item in self.all:
            result["menu"][item.category][item.name] = dict()
        
        for item in self.all:
            result["menu"][item.category][item.name]["Price"] = item.price
            result["menu"][item.category][item.name]["Options"] = item.options

        result["config"]["Sides Included"] = getattr(MenuEditor, "include_sides")
        result["config"]["Drinks Included"] = getattr(MenuEditor, "include_drinks")
        result["config"]["Two Sides"] = getattr(MenuEditor, "two_sides")
        result["config"]["No Addons"] = getattr(MenuEditor, "no_addons")
        return result

    def to_csv(self):
        return self.__repr__()

    def save(self, csv=False):
        if csv:
            with open(self.filename, "w") as fp:
                fp.write(self.to_csv())
        else:
            with open(self.filename, "w") as fp:
                json.dump(fp, self.to_dict())
    
    @classmethod
    def load(cls, new_menu):
        items = new_menu["menu"]
        config = new_menu["config"]

        for category in items:
            cls.menu[category] = items[category] # pylint: disable=E1101
        
        for conf in config:
            cls.config = config[conf]
        logger.info("Loaded new menu")



class Key(tk.Button):

    all_keys = list()
    shift = False

    def __init__(self, parent, char):
        super().__init__(parent,
                bd=2,
                relief=tk.RAISED,
                bg="black",
                fg="white")
        
        self.char = char
        self.target = None
        self.configure(text=self.char, command=self.on_press, font=("Courier", 12, "bold"))
        if self.char.strip() == "X":
            self.configure(state=tk.DISABLED, disabledforeground="black")
        Key.all_keys.append(self)
        
    def on_press(self):            
        if self.target is None:
            return
    
        char = self.char.strip()
        if Key.shift:
            char = char.upper()
    
        if char.lower() == "space":
            self.target.insert(tk.END, " ")
        elif char.lower() == "backspace":
            self.target.delete(len(self.target.get()) - 1, tk.END)
        elif char.lower() == "enter":
            for key in Key.all_keys:
                key.target = None
        elif char.lower() == "shift":
            Key.shift = True
            return
        else:
            self.target.insert(tk.END, char)
        
        Key.shift = False
   

class Keyboard(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.chars = {
            0: (" q "," w "," e "," r "," t "," y "," u "," i "," o "," p "),
            1: (" a "," s "," d "," f "," g "," h "," j "," k "," l "," + ",),
            2: (" z "," x "," c "," v "," b "," n "," m "," * "," / "," - ",),
            
        }
        self.key_frame = tk.Frame(self)
        self.key_frame.grid(row=0, column=0, sticky="nswe", columnspan=10)

        for row in self.chars:
            for i, char in enumerate(self.chars[row]):
                k = Key(self.key_frame, char)
                k.grid(row=row, column=i)
    
        shift = Key(self.key_frame, "  shift  ")
        shift.grid(row=3, column=0, columnspan=2, sticky="nswe")
        space = Key(self.key_frame, "        Space        ")
        space.grid(row=3, column=2, columnspan=4, sticky="nswe")
        enter = Key(self.key_frame, " Enter ")
        enter.grid(row=3, column=8, columnspan=2, sticky="nswe")
        backspace = Key(self.key_frame, "Backspace")
        backspace.grid(row=3, column=6, columnspan=2, sticky="nswe")
       
        self._target = None
    
    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, value):
        for key in Key.all_keys:
            key.target = value

