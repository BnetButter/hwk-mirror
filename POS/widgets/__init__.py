from tkinter import ttk
from lib import TabbedFrame
from lib import MenuWidget
from .menu_display import CategoryFrame
from .console import *


class MenuDisplay(TabbedFrame, metaclass=MenuWidget, device="POS"):
    
    tabfont = ("Courier", 20)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        style = ttk.Style(master=self)
        style.configure("TNotebook.Tab", font=self.tabfont, width=MenuDisplay.longest_category)
        for category in MenuDisplay.categories:
            self[category] = CategoryFrame(parent, category)

class OrderDisplay():
    pass

