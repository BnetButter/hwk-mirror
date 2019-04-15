import tkinter as tk
import lib

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
        self.toggle.grid(row=0, column=0, sticky="nswe")
