from tkinter import ttk
from functools import wraps, partial
from collections import UserDict, UserList
from io import StringIO
import asyncio
import tkinter as tk
import logging
from .data import log_info
from .data import GUI_STDERR

logger = logging.getLogger(GUI_STDERR)

class WidgetCache(UserList):

    def __init__(self, _class, parent, initial_size=10, *args, **kwargs):
        self.cls = partial(_class, parent, *args, **kwargs)
        self.data = [self.cls() for i in range(initial_size)]
        self.initial_size = initial_size
        self.size = initial_size
    
    def realloc(self, new_size):
        if new_size >= self.size:            
            self.size *= 2
            while len(self.data) < self.size:
                self.data.append(self.cls())

        elif (self.size / 4) >= new_size \
                and (self.size / 2) >= self.initial_size:
            self.size /= 2
            while len(self.data) > self.size:
                self.data.pop().destroy()

class LabelButton(tk.Label):

    def __init__(self, parent, text, command=lambda *args:None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.command = command
        self.configure(bd=2, relief=tk.RAISED)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def activate(self):
        self["fg"] = "black"
        self["relief"] = tk.RAISED
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def deactivate(self):
        self["fg"] = "grey26"
        self["relief"] = tk.GROOVE
        self.unbind("<Button-1>")
        self.unbind("<ButtonRelease-1>")

    def on_click(self, *args):
        self.configure(relief=tk.SUNKEN, fg="black")
    
    def on_release(self, *args):
        self.configure(relief=tk.RAISED, fg="black")
        self.command()
    


class ToggleSwitch(LabelButton):

    def __init__(self, parent, text, default="grey",state=False,
                config_true={"relief": tk.SUNKEN, "bg":"green"},
                config_false={"relief": tk.RAISED, "bg":"grey"}, **kwargs):
        super().__init__(parent, text, self._cmd, bg=default, **kwargs)
        self._state = None
        self.config_true = config_true
        self.config_false = config_false
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value:bool):
        self._state = value
        if value:
            self.configure(**self.config_true)
        else:
            self.configure(**self.config_false)
    
    def __bool__(self):
        return self.state
    
    def on_click(self, *args):
        pass
    
    def on_release(self, *args):
        self.command()
    
    def _cmd(self):
        if self.state:
            self.state = False
        else:
            self.state = True
    
    def reset(self):
        self.state = False

    

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
            anchor=tk.NW)
        
        self.interior.bind("<Configure>", self.configure_interior)
        self.canvas.bind("<Configure>", self.configure_canvas)
        self.scrollbar = vscrollbar
        self.mouse_position = 0

    def configure_scroll(self, event):
        self.canvas.config(scrollregion=f"0 0 {self.interior.winfo_reqwidth()} {self.interior.winfo_reqheight()}")

    def configure_interior(self, event):
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=f"0 0 {size[0]} {size[1]}")
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

class TabbedFrame(tk.Frame):
    """Frame widget with tabs"""
    
    def __init__(self, parent, *tabs, **kwargs):
        super().__init__(parent, **kwargs)
        assert all(isinstance(t, str) for t in tabs)
        self.style = ttk.Style(self)
        self.style.configure("TNotebook.Tab")
        self._notebook = ttk.Notebook(self, style="TNotebook")
        self.data = {
            name: tk.Frame(self._notebook)
            for name in tabs}
        
        for name in self.data:
            self._notebook.add(self.data[name], text=name)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._notebook.grid(row=0, column=0, sticky="nswe")
    
    def __setitem__(self, key, value):
        self.data[key] = value
        self._notebook.add(self.data[key], text=key)
    
    def __getitem__(self, key):
        return self.data[key]


def write_enable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        self["state"] = tk.NORMAL
        func(*args, **kwargs)
        self["state"] = tk.DISABLED
    return wrapper



