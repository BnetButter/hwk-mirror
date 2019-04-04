from tkinter import ttk
from lib import TabbedFrame
from lib import MenuWidget
from lib import stdout
from .menu_display import CategoryFrame
from .console import *
from .order_display import *
from .menu_editor import *
from .price_display import PriceDisplay
from .checkout_display import CheckoutFrame
from .network_status import NetworkStatus
from logging import getLogger
from .shutdown_button import *
from .titlebar import titlebar
from .progress_tab import ProgressFrame
from .order import Order, NewOrder

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
        order_frame = OrdersFrame(self)
        checkout_frame = CheckoutFrame(self)
        progress_frame = ProgressFrame(self)
    
        self["Orders    "] = order_frame
        self["Checkout  "] = checkout_frame
        self["Processing"] = progress_frame

        order_frame.update_order_list()
        checkout_frame.update_order_list()
        progress_frame.update_order_status()