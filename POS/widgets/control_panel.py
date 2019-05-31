import tkinter as tk
import lib
import functools

class ToggleMenuMode(lib.ToggleSwitch):

    def __init__(self, parent, menu_display, editor_display, **kwargs):
        super().__init__(parent, "select",
            config_true={"relief": tk.SUNKEN, 
                        "bg": "white smoke",
                        "text":"edit"}, 
            config_false={"relief": tk.SUNKEN,
                        "bg": "white smoke",
                        "text":"select"},
            width=7, **kwargs)

        self.menu_display = menu_display
        self.menu_editor = editor_display

    def _cmd(self):
        if self.state:
            self.state = False
            self.menu_display.instance.lift()
        else:
            self.state = True
            self.menu_editor.instance.lift()


class ToggleFrame(tk.Frame, metaclass=lib.WidgetType, device="POS"):
    font = ("Courier", 12)

    def __init__(self, parent, menudisplay, editordisplay, **kwargs):
        super().__init__(parent, **kwargs)
        label = tk.Label(self, text="Menu Mode: ", font=self.font)
        toggle = ToggleMenuMode(self, menudisplay, editordisplay, font=self.font)
        label.grid(row=0, column=0, sticky="nswe")
        toggle.grid(row=0, column=1, sticky="nswe", ipadx=4)


class ControlPanel(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
    
    def add_mode_toggle(self, menudisplay, editordisplay):
        self.toggle = ToggleFrame(self, menudisplay, editordisplay)
        self.toggle.grid(row=0, column=0, sticky="nswe", pady=3)
    
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