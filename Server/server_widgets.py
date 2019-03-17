from lib import gettime
from lib import WidgetType
from lib import AsyncWindow
from lib import update
from lib import LabelButton
from tkinter import ttk
from time import strftime, localtime
from functools import partial
import tkinter as tk
import subprocess
import asyncio

class TimeEntry(tk.Entry):
    pass    

class ServerTime(tk.Frame, metaclass=WidgetType, device="Server"):
    font = ("Courier", 14)
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        label = tk.Label(self, text="Current Time: ", font=self.font)
        variable = tk.StringVar(self)
        entry = tk.Entry(self, textvariable=variable,
                font=self.font,
                state=tk.DISABLED,
                disabledforeground="black",
                disabledbackground="white")
        label.grid(row=0, column=0, sticky="nswe")
        entry.grid(row=0, column=1, sticky="nswe")
        self.set = variable.set
        self.get = variable.get
        AsyncWindow.append(self.update_time)

    async def update_time(self):
        while True:
            self.set(gettime())
            await asyncio.sleep(1)

symbol = lambda parent, symbol, **kwargs: tk.Label(parent, text=symbol, **kwargs)



class TimeVariable(tuple):

    def __new__(cls, parent, font=("Courier", 14)):

        lc = localtime()
        year = int(lc[0]) - 5
        year = [str(year + i) for i in range(10)]
        month = [str(1 + i) for i in range(12)]
        hour = [str(1 + i) for i in range(12)]
    
        year = ttk.Combobox(parent, values=year, width=5, font=font)
        year.set(lc[0])

        month = ttk.Combobox(parent, values=month, width=3, font=font)
        month.set(lc[1])

        day_var = tk.StringVar(parent)
        day_var.set(lc[2])
        day = tk.Entry(parent, textvariable=day_var, width=3, font=font)
        object.__setattr__(day, "set", day_var.set)
        object.__setattr__(day, "get", day_var.get)
        
        
        hour = ttk.Combobox(parent, values=hour, width=3, font=font)
        hour.set(strftime("%I", lc))
        
        minute_var = tk.StringVar(parent)
        minute_var.set(lc[4])
        minute = tk.Entry(parent, textvariable=minute_var, width=2, font=font)
        object.__setattr__(minute, "set", minute_var.set)
        object.__setattr__(minute, "get", minute_var.get)
    

        ampm = ttk.Combobox(parent, values=["AM", "PM"], width=3, font=font)
        ampm.set("AM")

        return super().__new__(cls, (month, day, year, hour, minute, ampm))

class EditTime(tk.Frame, metaclass=WidgetType, device="Server"):
    font=("Courier", 12)
    
    
    

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.variables = TimeVariable(self)
        labels = ["MM", "DD", "YYYY", "HH", "MM", "AM/PM"]
        labels = [tk.Label(self, font=self.font, text=label) for label in labels]
        for i, label in enumerate(labels):
            label.grid(row=0, column=i, sticky="w")
            self.variables[i].grid(row=1, column=i, sticky="w")

        confirm = LabelButton(self, "Set Time", command=self.set_time)
        confirm.grid(row=1, column=6)

    def set_time(self):
        fmt_date = "sudo date +%Y%m%d -s \"{}{:02d}{:02d}\""
        fmt_time = "sudo date +%T -s \"{:02d}:{:02d}:00\""

        if self.ampm == "PM":
            hour = int(self.hour) + 12
        else:
            hour = int(self.hour)
        
        result = subprocess.call(fmt_date.format(self.year, int(self.month), int(self.day)), shell=True)
        if result:
            raise OSError
        
        result = subprocess.call(fmt_time.format(hour, int(self.minute)), shell=True)
        if result:
            raise OSError
    
        self.grid_remove()

    @property
    def month(self):
        return self.variables[0].get()
    
    @property
    def day(self):
        return self.variables[1].get()
    
    @property
    def year(self):
        return self.variables[2].get()
    
    @property
    def hour(self):
        return self.variables[3].get()
    
    @property
    def minute(self):
        return self.variables[4].get()
    
    @property
    def ampm(self):
        return self.variables[5].get()

class ServerFrame(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        current_time = ServerTime(self, bd=2)    
        current_time.grid(row=0, column=0, pady=5, padx=5, sticky="nswe")
        edittime = EditTime(self)
        button = LabelButton(self, text="Edit", 
                command=partial(edittime.grid, 
                        row=1,
                        column=0,
                        pady=5,
                        padx=5), font=current_time.font)

        button.grid(row=0, column=1, pady=5, padx=5, sticky="nswe")
        confirm = LabelButton(self, text="Confirm", bg="green", command=AsyncWindow.exit)
        confirm.grid(row=2, column=0)

        