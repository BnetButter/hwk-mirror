from lib import MenuType
from lib import WidgetType
from lib import LOGPATH
from io import StringIO
import tkinter as tk
import subprocess
import logging

class Output(tk.Text):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=80, bg="grey26", fg="white", state=tk.DISABLED, **kwargs)
    
    def write(self, content):
        content = content.decode('utf-8')
        self.configure(state=tk.NORMAL)
        self.insert(tk.END, content)
        self.configure(state=tk.DISABLED)
    
    def read(self, start=0, end=tk.END):
        return self.get(start, end)

class Input(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        var = tk.StringVar(self)
        label = tk.Label(self, text="$ ", width=2, bg="grey26", fg="white", relief=tk.FLAT, bd=0)
        self.entry = entry = tk.Entry(self, 
                width=78,
                bg="grey26",
                fg="white",
                relief=tk.FLAT,
                bd=0,
                highlightthickness=0,
                textvariable=var,
                insertbackground="white")
        
        label.grid(row=1, column=0)
        entry.grid(row=1, column=1)
        self.set = var.set
        self.get = var.get
        entry.bind("<Return>", self.on_enter)
     
    def on_enter(self, *args):
        self.set("")

class Terminal(Input):

    def __init__(self, parent, interpreter='/bin/bash', width=80, **kwargs):
        super().__init__(parent, **kwargs)
        scrollbar = tk.Scrollbar(self)
        self.interpreter = interpreter
        self.output = Output(self, relief=tk.FLAT, highlightthickness=0, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.output.yview)
        scrollbar.grid(row=0, column=3, rowspan=2, sticky="ns")
        self.output.grid(row=0, column=0, columnspan=2)
        self.read = self.output.read

    def on_enter(self, *args):
        process = subprocess.Popen(self.interpreter, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        result = process.communicate(self.get().encode('utf-8'))[subprocess.STDOUT]
        self.output.write(result)
        super().on_enter(*args)

from lib.metaclass import WidgetType
from lib.stream import StreamType
from lib import stderr
from lib import stdout

# resolve metaclass conflict
class ConsoleType(StreamType, WidgetType):
    def __new__(cls, name, bases, attr, stream=None, device="POS"):
        return super().__new__(cls, name, bases, attr, stream=stream, device=device)

class console_stdout(tk.Text, metaclass=ConsoleType):

    font = ("Courier",10)
    font_height = 6

    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                height=self.font_height,
                highlightthickness=0,
                bd=0,
                bg="grey26",
                fg="white",
                font=self.font,
                **kwargs)

        # console_stdout.stream defined by ConsoleType
        # add existing contents of stream to tk.Text widget
        self.insert(tk.END, self.stream.read()) # pylint: disable=E1101
        self['state'] = tk.DISABLED

        # instance takes ownership of the stream
        self.set_stream() # pylint: disable=E1101


# exactly the same as console_stdout but instance takes ownership of stderr
class console_stderr(console_stdout, metaclass=ConsoleType, stream=stderr):
    font = ("Courier", 10)
    font_height = 6
    font_width = 80