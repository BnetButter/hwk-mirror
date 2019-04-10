import tkinter as tk
import lib

class ToggleMenuMode(lib.ToggleSwitch):

    def __init__(self, parent, menu_display, editor_display, **kwargs):
        super().__init__(parent, "Select Mode", width=12, **kwargs)
        self.menu_display = menu_display
        self.menu_editor = editor_display
        self._cmd()
        
    def _cmd(self):
        if self.state:
            self["text"] = "Edit Mode"
            self["bg"] = "yellow"
            self.menu_editor.instance.lift()
            self.state = False
        else:
            self["text"] = "Select Mode"
            self.menu_display.instance.lift()
            self.state = True
