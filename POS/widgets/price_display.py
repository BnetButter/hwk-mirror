from lib import WidgetType
from .order import Order
from lib import AsyncTk, update
import tkinter as tk
import asyncio


class PriceEntry(tk.Frame, metaclass=WidgetType, device="POS"):
    font=("Courier", 20)

    def __init__(self, parent, text, textvariable, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = tk.Label(self, 
                text=text,
                font=self.font,
                anchor=tk.E)
        
        self.entry = tk.Entry(self,
                textvariable=textvariable,
                font=self.font,
                width=len("$ 000.00"),
                state=tk.DISABLED,
                disabledforeground="black",
                disabledbackground="white")

        self.label.grid(row=0, column=0, sticky="nswe")
        self.entry.grid(row=0, column=1, sticky="nswe")

class PriceDisplay(tk.Frame):
    """displays subtotal, tax, and total for a given order"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.subtotal_var = tk.StringVar(self)
        self.tax_var = tk.StringVar(self)
        self.total_var = tk.StringVar(self)

        PriceEntry(self, "Subtotal", self.subtotal_var
                ).grid(sticky="nswe",
                    padx=5,
                    columnspan=2)
        
        PriceEntry(self, "     Tax", self.tax_var
                ).grid(row=1,
                    sticky="nswe",
                    padx=5,
                    columnspan=2)
    
        PriceEntry(self, "   Total", self.total_var
                ).grid(row=2,
                    sticky="nswe",
                    padx=5,
                    columnspan=2)
        
        self.update()

    @update
    def update(self):
        fmt = "$ {:.2f}"
        self.subtotal_var.set(fmt.format(Order().subtotal / 100))
        self.tax_var.set(fmt.format(Order().tax / 100))
        self.total_var.set(fmt.format(Order().total / 100))
