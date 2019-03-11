from tkinter import ttk
import tkinter as tk
from collections import UserDict
from io import StringIO
import lib

class TextWidget(tk.Frame):
    font = ("Courier", 12)
    
class LabelButton(tk.Label):

    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.command = command
        self.configure(bd=2, relief=tk.RAISED)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def deactivate(self):
        self.unbind("<Button-1>")
        self.unbind("<ButtonRelease-1>")

    def on_click(self, *args):
        self.configure(relief=tk.SUNKEN)
    
    def on_release(self, *args):
        self.configure(relief=tk.RAISED)
        self.command()

class ToggleSwitch(LabelButton):

    def __init__(self, parent, text, default="grey", **kwargs):
        super().__init__(parent, text, self._cmd, bg=default, **kwargs)
        self.state = False

    def __bool__(self):
        return self.state

    @property
    def is_on(self):
        return self.state == True
    
    @property
    def is_off(self):
        return self.state == False
    
    def on_click(self, *args):
        pass
    
    def on_release(self, *args):
        self.command()
    
    def _cmd(self):
        if self.state:
            self.state = False
            self.configure(relief=tk.RAISED, bg="grey")
        else:
            self.state = True
            self.configure(relief=tk.SUNKEN, bg="green")
    
    def reset(self):
        self.state = False
        self.configure(relief=tk.RAISED, bg="grey")

    

class EntryVariable(tk.Entry):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._sv = tk.StringVar(self)
        self.configure(textvariable=self._sv)

    def __call__(self):
        return self._sv       
    
    def set(self, value:str):
        self._sv.set(value)
    
    def get(self):
        return self._sv.get()


class EntryPreset(EntryVariable):
    """Entry with preset value"""
    def __init__(self, parent, preset, default=False, **kwargs):
        assert isinstance(preset, str)
        super().__init__(parent, **kwargs)
        self.preset = preset
        self.default = default
        self.set(preset)
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)


    def get(self):
        result = super().get()
        if result == self.preset:
            if self.default:
                return self.preset
            else:
                return ""
        return result

    def _focus_in(self, *args):
        if super().get() == self.preset:
            self.set("")

    def _focus_out(self, *args):
        if super().get() == "":
            self.set(self.preset)


class ScrollFrame(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0,*kwargs)
       
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
      
        self.canvas = canvas = tk.Canvas(self, bd=2, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=canvas.yview)
        
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)        
        self.interior = interior = tk.Frame(canvas)

        self.interior_id = canvas.create_window(0, 0,
            window=interior,
            anchor=tk.NW
            )
        self.canvas.bind('<Configure>', self.configure_interior)
        self.interior.bind("<Configure>", self.configure_canvas)
        self.scrollbar = vscrollbar
        self.mouse_position = 0

    def configure_scroll(self, event):
        self.canvas.config(scrollregion=f"0 0 {self.interior.winfo_reqwidth()} {self.interior.winfo_reqheight()}")

    def configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width(), height=self.canvas.winfo_height())
    
    def configure_interior(self, event):
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=f"0 0 {size[0]} {size[1]}")
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth(), height=self.interior.winfo_reqheight())


class TabbedFrame(tk.Frame):
    """Frame widget with tabs"""
    
    def __init__(self, parent, *tabs, **kwargs):
        super().__init__(parent, **kwargs)
        assert all(isinstance(t, str) for t in tabs)
        self._notebook = ttk.Notebook(self)
        self.data = {
            name: tk.Frame(self._notebook)
            for name in tabs}
        
        for name in self.data:
            self._notebook.add(self.data[name], text=name)
        self._notebook.grid(row=0, column=0, sticky="nswe")
    
    def __setitem__(self, key, value):
        self.data[key] = value
        self._notebook.add(self.data[key], text=key)
    
    def __getitem__(self, key):
        return self.data[key]