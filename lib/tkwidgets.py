from tkinter import ttk
from functools import wraps, partial
from collections import UserDict, UserList
from io import StringIO
from time import localtime, strftime

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
    null_cmd = lambda *args: None
    def __init__(self, parent, text, command=None, relief=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        if command is None:
            command = self.null_cmd
        if relief is None:
            relief = tk.RAISED
        
        self.active_config = {"fg":"black", "relief":tk.RAISED}
        self.disabled_config = {"fg":"grey26", "relief":tk.GROOVE}
        self.command = command
        self.configure(bd=2, relief=relief)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self._active = True

    def activate(self):
        self.configure(**self.active_config)
        self._active = True

    def deactivate(self):
        self.configure(**self.disabled_config)
        self._active = False
    
    def on_click(self, *args):
        if self._active:
            self.configure(relief=tk.SUNKEN, fg="black")
    
    def on_release(self, *args):
        if self._active:
            self.configure(relief=tk.RAISED, fg="black")
            self.command()


class MessageButton(tk.Message):
    null_cmd = lambda: None

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = type(self).null_cmd
        self._active = True
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.configure(relief=tk.SUNKEN)

    def on_release(self, event):
        self.configure(relief=tk.RAISED)
        self.command()
    
    def activate(self):
        self.configure(relief=tk.RAISED, fg="black")
        self._active = True

    def deactivate(self):
        self.configure(relief=tk.GROOVE, fg="grey26")
        self._active = False

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
        return bool(self.state)
    
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
        super().__init__(parent, highlightthickness=0, **kwargs)
       
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
        self._tab_ids = {}
        for name in self.data:
            self._notebook.add(self.data[name], text=name)
            self._tab_ids[name] = self._notebook.tabs()[-1]
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._notebook.grid(row=0, column=0, sticky="nswe")    

    def __setitem__(self, key, value):
        self.data[key] = value
        self._notebook.add(self.data[key], text=key)
        self._tab_ids[key] = self._notebook.tabs()[-1]
    
    def __getitem__(self, key):
        return self.data[key]
    
    def current(self):
        return self._notebook.tab(self._notebook.select(), "text")
    
    def select(self, key):
        self._notebook.select(self.data[key])

    def tab_id(self, key):
        return self._tab_ids[key]

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def pop(self, key):
        frame = self.data.pop(key)
        self._notebook.forget(self._tab_ids.pop(key))
        return frame

class PriceInput(tk.Entry):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._value = kwargs.get("textvariable")
        if self._value is None:
            self._value = tk.StringVar(parent)
            self._value.set("0.00")
        
        self.configure(
                textvariable=self._value,
                state=tk.DISABLED,
                disabledforeground="black",
                disabledbackground="white")

    def set_keypress_bind(self, target,
            condition=lambda *args:False,
            on_enter=lambda:None):
        
        def on_event(event):            
            if not condition():
                return
            
            if not (event.keysym in type(self).valid_keysyms
                    or event.keysym in type(self).numlock_switch):
                return

            char = event.char
            if event.keysym in type(self).numlock_switch:
                char = type(self).numlock_switch[event.keysym]

            if event.keysym == "KP_Enter":
                return on_enter()
            elif event.keysym == "BackSpace":
                self.value = 0
                return
            self.value += char
        
        return target.bind("<Key>", on_event, "+")

    @property
    def value(self):
        return self._value.get().replace(".", "")
    
    @value.setter
    def value(self, val):
        val = int(val)
        self._value.set("{:.2f}".format(val / 100))
    
    valid_keysyms = [f"KP_{i}" for i in range(10)]
    valid_keysyms.extend(("KP_Enter", "BackSpace"))

    # input numbers even without numlock
    numlock_switch = {
            "KP_Insert": "0",
            "KP_Delete": "00",
            "KP_Decimal":"00",
            "KP_End":    "1",
            "KP_Down":   "2",
            "KP_Next":   "3",
            "KP_Left":   "4",
            "KP_Begin":  "5",
            "KP_Right":  "6",
            "KP_Home":   "7",
            "KP_Up":     "8",
            "KP_Prior":  "9",
        }        

def write_enable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        self["state"] = tk.NORMAL
        func(*args, **kwargs)
        self["state"] = tk.DISABLED
    return wrapper

class Key(tk.Button):
    ENTER = "\u23CE"
    DEL   = "\u232B"
    LEFT  = "\u2190"
    RIGHT = "\u2192"

    all_keys = list()
    shift = False
    def __init__(self, parent, char, font=("Courier", 14)):
        super().__init__(parent,
                bd=2,
                relief=tk.RAISED,
                bg="black",
                fg="white",
                font=font)

        if not char.strip():
            self["state"] = tk.DISABLED    
            self["relief"] = tk.FLAT
            self["bd"] = 0
        
        self.char = char
        self.target = None
        self.configure(text=self.char, command=self.on_press)
        
        Key.all_keys.append(self)

    def on_press(self):            
        if self.target is None:
            return
    
        char = self.char.strip()
        if Key.shift:
            char = char.upper()
        
        if char.lower() == "space":
            self.target.insert(tk.INSERT, " ")
        
        elif char.lower() == Key.DEL:
            self.target.delete(self.target.index(tk.INSERT) - 1, tk.INSERT)
        
        elif char.lower() == Key.ENTER:
            self.target.tk_focusNext().focus()

        elif char.lower() == Key.LEFT:
            idx = self.target.index(tk.INSERT) - 1
            self.target.icursor(idx)
        
        elif char.lower() == Key.RIGHT:
            idx = self.target.index(tk.INSERT) + 1
            self.target.icursor(idx)

        elif char.lower() == "shift":
            Key.shift = True
            return
        else:
            self.target.insert(tk.INSERT, char)
        
        Key.shift = False

class Keyboard(tk.Frame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        L = Key.LEFT
        R = Key.RIGHT
        self.chars = {
            0: ("q","w","e","r","t","y","u","i","o","p", "", "","7","8","9","-"),
            1: ("a","s","d","f","g","h","j","k","l", "", "", "","4","5","6","+"),
            2: ("z","x","c","v","b","n","m",",",".",  L,  R, "","1","2","3","*"),
            3: ( "", "", "", "", "", "", "", "", "", "", "", "", "", "","." ,"/")}

        for i in range(15):
            self.grid_columnconfigure(i, weight=1)
        for row in self.chars:
            for i, char in enumerate(self.chars[row]):
                if char:
                    k = Key(self, char)
                    k.grid(row=row, column=i, sticky="nswe")
    
        shift = Key(self, "Shift")
        shift.grid(row=3, column=0, columnspan=2, sticky="nswe")
        space = Key(self, "Space")
        space.grid(row=3, column=2, columnspan=4, sticky="nswe")
        enter = Key(self, Key.ENTER)
        enter.grid(row=1, column=9, columnspan=2, sticky="nswe")
        back = Key(self, Key.DEL)
        back.grid(row=0, column=10, sticky="nswe")

        tk.Label(self, text=" ", bg="black").grid(row=3, column=6, columnspan=5, sticky="nswe", ipadx=2)
        tk.Label(self, text=" ", bg="black").grid(row=0, column=11, rowspan=4, sticky="nswe", ipadx=14)
        Key(self, "0").grid(row=3, column=12, columnspan=2, sticky="nswe")
        self._target = None

    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, value):
        for key in Key.all_keys:
            key.target = value

class NumpadKeyboard(tk.Frame):

    def __init__(self, parent, font=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._target = None
        self.chars = {
            0:( "", "", Key.DEL),
            1:("7","8","9"),
            2:("4","5","6"),
            3:("1","2","3"),
            4:("", "", "."),
        }
        for row in self.chars:
            for i, char in enumerate(self.chars[row]):
                Key(self, char, font=font).grid(row=row, column=i, sticky="nswe")
        Key(self, "0", font=font).grid(row=4, column=0, columnspan=2, sticky="nswe")
    
    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, value):
        self._target = value
        for key in Key.all_keys:
            key.target = value

class StatusIndicator(ToggleSwitch):
    
    def __init__(self, parent, text, font=None, **kwargs):
        if font is None:
            font = ("Courier", 10)
        super().__init__(parent, text,
                config_true={"relief": tk.SUNKEN,"bg":"green3"},
                config_false={"relief": tk.RAISED, "bg":"red"}, font=font, **kwargs)
        self.state = False
        self.disabled_config = {"fg":"black"}

    def set(self, value:bool):
        if value is None:
            value = False
        self.state = value


class Clock(tk.Entry):

    def __init__(self, parent, **kwargs):
        super().__init__(parent,
            width=11,
            state=tk.DISABLED,
            disabledbackground="white",
            disabledforeground="black",
            relief=tk.RIDGE, **kwargs)
        self._time = tk.StringVar(self)
        self["textvariable"] = self._time
    
    async def update(self):
        while True:
            self._time.set(strftime("%I:%M:%S %p", localtime()))
            await asyncio.sleep(1)