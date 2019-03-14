from tkinter import ttk
from lib import TabbedFrame
from lib import MenuWidget
from lib import stdout
from .menu_display import CategoryFrame
from .console import *
from .order_display import *
from .menu_editor import *
from .price_display import PriceDisplay
from logging import getLogger
from copy import deepcopy

class MenuDisplay(TabbedFrame, metaclass=MenuWidget, device="POS"):
    
    tabfont = ("Courier", 14)
    __instance = None

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.style.configure("MenuDisplay.TNotebook.Tab",
                font=self.tabfont,
                padding=5)
        
        self._notebook.configure(style="MenuDisplay.TNotebook")
        for category in MenuDisplay.categories:
            self[category] = CategoryFrame(self, category)

        
        MenuDisplay.__instance = self

    @classmethod
    def reinstance(cls, parent):
        current = cls.__instance
        result = object.__new__(MenuDisplay)
        MenuDisplay.__init__(result, parent)
        result.grid(**(current.grid_info()))
        stdout.write("Reinstanced menu\n")
        current.destroy()
        return result
        
class OrderDisplay(TabbedFrame, metaclass=MenuWidget, device="POS"):
    tabfont = ("Courier", 14)
    __instance = None
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.style.configure("OrderDisplay.TNotebook.Tab",
            font=self.tabfont,
            padding=5)
        self._notebook.configure(style="OrderDisplay.TNotebook")
        self["Orders"] = OrdersFrame(self)

"""
    def configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width(), height=self.canvas.winfo_height())
    
    def configure_interior(self, event):
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=f"0 0 {size[0]} {size[1]}")
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth(), height=self.interior.winfo_reqheight())

"""