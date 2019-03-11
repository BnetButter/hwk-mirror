from lib import tkwidgets
from lib.tkwidgets import TextWidget
from lib.tkwidgets import LabelButton
from lib import MenuType
from lib import WidgetType
from lib import MenuWidget
from lib import MenuItem
from lib import Order
import lib
import tkinter as tk

class DropDown(tk.Frame, metaclass=MenuWidget, device="POS"):
    """Drop down menu to select sides and drinks"""
    menu_font = ("Courier", 14)
    title_font = ("Courier", 16)
    
    def __init__(self, parent, addon, state=None):
        super().__init__(parent)
        if state is None:
            state = tk.ACTIVE
        
        self.title = addon
        self.variable = tk.StringVar(self)
        self.variable.set(self.title)
        self.items = DropDown.category(addon)

        self.dropdown = tk.OptionMenu(self, self.variable, *(item[1] for item in self.items))
        self.menu = tk.OptionMenu.nametowidget(self.dropdown, self.dropdown.menuname)
        self.menu.configure(font=self.menu_font)
        self.dropdown.configure(width=DropDown.longest_addon, font=self.title_font, state=state)
        self.dropdown.grid(row=0, column=0, sticky="nswe")

    def configure_dropdown(self, **kwargs):
        self.dropdown.configure(**kwargs)
    
    def configure_menu(self, **kwargs):
        self.menu.configure(**kwargs)

    def reset(self):
        self.variable.set(self.title)

    def getvalue(self):
        selected_value = self.variable.get()
        for item in self.items:
            if selected_value == item.name:
                return item
        return MenuItem("", "", 0, {})

    def printvalue(self):
        print(self.getvalue())


class Options(tk.Frame, metaclass=MenuWidget, device="POS"):
    font = ("Courier", 12)
    width = 18

    def __init__(self, parent, menu_item, **kwargs):
        super().__init__(parent, **kwargs)
        self.has_options = False
        if menu_item.options:
            self.has_options = True
            self.option_toggles = [
                    tkwidgets.ToggleSwitch(self, text,
                        font=self.font,
                        width=self.width)
                        for text in menu_item.options
                    ]
            row = 0
            column = 0
            for item in self.option_toggles:
                # two options per row
                if column == 2:
                    column = 0
                    row += 1
                item.grid(row=row, column=column, sticky='w')
                column += 1

    def __bool__(self):
        return self.has_options

    def getvalue(self):        
        if self.has_options:
            return [item["text"] for item in self.option_toggles if item]
        return []

    def printvalue(self):
        print(self.getvalue())

    def reset(self):
        if self.has_options:
            [item.reset() for item in self.option_toggles]

class AddonOptions(tk.Toplevel, metaclass=WidgetType, device="POS"):
    font = ("Courier", 12)

    def __init__(self, parent, order, **kwargs):
        super().__init__(parent, **kwargs)
        self.wm_title(string="Configure Addon")

        self.addon1 = addon1 = order.addon1
        self.addon2 = addon2 = order.addon2
        self.option_frame1 = Options(self, addon1)
        self.option_frame2 = Options(self, addon2)
        
        if addon1.options:
            self.label(addon1.name).pack()
            self.option_frame1.pack()
        if addon2.options:
            self.label(addon2.name).pack()
            self.option_frame2.pack()
        self.protocol("WM_DELETE_WINDOW", self.close)
        
        done = tk.Button(self, text="Done", bg="green", command=self.close)
        close = tk.Button(self, text="Close", bg="red", command=self.destroy)
        close.pack(pady=10, padx=5, side=tk.LEFT)
        done.pack(pady=10, padx=5, side=tk.LEFT)
    def label(self, name):
        return tk.Label(self,
                text=f"Select options for {name}", 
                font=self.font)

    def close(self, *args):

        self.addon1.selected_options = self.option_frame1.getvalue()
        self.addon2.selected_options = self.option_frame2.getvalue()
        self.destroy()

class OptionButton(LabelButton):
    """Button widget that grid/ungrids option frame"""

    def __init__(self, parent, option_frame, **kwargs):    
        super().__init__(parent, "options")
        self.gridded_frame = False
        self.option_frame = option_frame
        self.inactive_config = {"bg":"green", "relief":tk.RAISED}
        self.has_options_config = {"bg": "white smoke", "relief": tk.SUNKEN}
        self.configure(bg="green")

    def on_release(self, *args):
        if self.gridded_frame:
            self.gridded_frame = False
            self.configure(**self.inactive_config)
            self.option_frame.grid_forget()
        else:
            self.gridded_frame = True
            self.configure(**self.has_options_config)
            self.option_frame.grid(
                    row=2,
                    column=1,
                    columnspan=2)

    def reset(self):
        self.option_frame.grid_forget()
        self.configure(**self.inactive_config)
        self.gridded_frame = False

        
class ItemSelector(tk.Frame, metaclass=MenuWidget, device="POS"):
    font = ("Courier", 12)
    
    def __init__(self, parent, menu_item, **kwargs):
        super().__init__(parent, **kwargs)
        self.menu_item = menu_item
        self.label = tk.Label(self, 
                text=menu_item.name,
                font=self.font,
                width=ItemSelector.longest_item,
                anchor="w")

        self.options_frame = Options(self, menu_item)
        self.options_button = OptionButton(self, self.options_frame, 
                font=(self.font[0], int(self.font[1]) * (2/3)))
        
        if menu_item.category not in ItemSelector.two_sides:
            title1 = "Sides"
            title2 = "Drinks"
        else:
            title1 = "Sides"
            title2 = "Sides"
        
        if menu_item.category in ItemSelector.no_addons:
            state = tk.DISABLED
        else:
            state = None
        
        self.dropdown1 = DropDown(self, title1, state=state)
        self.dropdown2 = DropDown(self, title2, state=state)

        self.add_button = tk.Button(self, text="+", command=self._button_callback)
        self.add_button.configure(bg="green")
        self._grid()
    
    def _grid(self):
        self.grid_rowconfigure(0, weight=1)
        self.label.grid(row=0, column=0, rowspan=2, sticky="w")

        if self.options_frame:
            self.options_button.grid(row=1, column=0, sticky="ne")
            self.dropdown1.grid(row=0, column=1, rowspan=2, sticky="nwe")
            self.dropdown2.grid(row=0, column=2, rowspan=2, sticky="nwe")
            self.add_button.grid(row=0, column=3, rowspan=2, sticky="nswe")
        else:
            self.dropdown1.grid(row=0, column=1, sticky="nswe")
            self.dropdown2.grid(row=0, column=2, sticky="nswe")
            self.add_button.grid(row=0,column=3, sticky="nswe")
    
    def _button_callback(self, *args):

        addon1 = self.dropdown1.getvalue()
        addon2 = self.dropdown2.getvalue()
        selected_options = self.options_frame.getvalue()

        Order()(self.menu_item, 
                addon1,
                addon2,
                selected_options)

        if addon1.options or addon2.options:
            AddonOptions(self, Order()[-1])

    def reset(self):
        self.dropdown1.reset()
        self.dropdown2.reset()
        self.options_frame.reset()
        self.options_button.reset()
    
class CategoryFrame(tkwidgets.ScrollFrame, metaclass=MenuType):

    def __init__(self, parent, category, **kwargs):
        super().__init__(parent, **kwargs)
        self.item_frames = [
                ItemSelector(self.interior, item) for item in CategoryFrame.category(category)]
        for i, item in enumerate(self.item_frames):
            self.interior.grid_columnconfigure(0, weight=1)
            item.grid(row=i, column=0, columnspan=4, sticky="nswe")
        
        self.configure_canvas(0)
        self.configure_interior(0)
