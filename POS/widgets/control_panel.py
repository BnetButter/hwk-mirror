import tkinter as tk
import lib
import functools

class FrameSwitch(lib.LabelButton):

    def __init__(self, parent, initial, **kwargs):
        super().__init__(parent,initial, 
                font=("Courier", 12),
                width=8,
                bg="yellow")
        self.data = [(txt, frame) for txt, frame in zip(kwargs.keys(), kwargs.values())]
        self.command = self.switch
        self.mode = 1

    def switch(self):
        if self.mode == len(self.data):
            self.mode = 0
        
        self["text"] = self.data[self.mode][0]
        self.data[self.mode][1].instance.lift()
        self.mode += 1
        return self.data[self.mode - 1]
    
    def select(self, cls):
        
        for i, (txt, framecls) in enumerate(self.data):
            if cls == framecls:
                self["text"] = txt
                framecls.instance.lift()
                self.mode = i + 1
                return



class ToggleFrame(tk.Frame, metaclass=lib.WidgetType, device="POS"):
    font = ("Courier", 12)

    def __init__(self, parent, initial, **kwargs):
        super().__init__(parent)
        label = tk.Label(self, text="Menu Mode: ", font=self.font)
        label.grid(row=0, column=0, sticky="nswe")
        self.switcher = FrameSwitch(self, initial, **kwargs)
        self.switcher.grid(row=0, column=1, sticky="nswe", ipadx=4)


class ControlPanel(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.select = None

    def add_mode_toggle(self, initial, **frames):
        self.toggle = ToggleFrame(self, initial, **frames)
        self.toggle.grid(row=0, column=0, sticky="nswe", pady=3)
        self.select = self.toggle.switcher.select
    def add_invoice_printer(self):
        command = functools.partial(lib.AsyncTk().forward, "print_invoice")
        label = tk.Label(self, text="Invoice Receipt", font=ToggleFrame.font)
        button = lib.LabelButton(self, text="Print", command=command, font=ToggleFrame.font)
        label.grid(row=0, column=1, sticky="nswe", padx=3, pady=3)
        button.grid(row=0, column=2, sticky="nswe", padx=3, pady=3)
    
    def daily_sales_printer(self):
        command=functools.partial(lib.AsyncTk().forward, "print_daily_sales")
        label = tk.Label(self, text="Daily Sales", font=ToggleFrame.font)
        button = lib.LabelButton(self, text="Print", command=command, font=ToggleFrame.font)
        label.grid(row=1, column=1, sticky="nswe", padx=3, pady=3)
        button.grid(row=1, column=2, sticky="nswe", padx=3, pady=3)
    
    def open_drawer(self):
        label = lib.LabelButton(self,
                    text="Open Drawer",
                    font=ToggleFrame.font, 
                    command=functools.partial(lib.AsyncTk().forward, "open_drawer"))
        label.grid(row=0, column=3, sticky="nswe", padx=3, pady=3, ipadx=5)