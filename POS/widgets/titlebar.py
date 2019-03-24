from functools import partial
from time import strftime, localtime
from lib import AsyncTk, update
import asyncio
import lib
import tkinter as tk
import sys
import os

class StatusIndicator(lib.ToggleSwitch, metaclass=lib.WidgetType, device="POS"):
    font=("Courier", 10)
    
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, text,
                config_true={"relief": tk.SUNKEN,"bg":"green3"},
                config_false={"relief": tk.RAISED, "bg":"red"},
                font=self.font)
        self.state = False
        
        
        # disable user control but not the widget itself
        self.deactivate()
    
    def set(self, value:bool):
        self.state = value        

class NetworkStatus(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # green if POS device connected to network
        self.network_indicator = StatusIndicator(self, "Network", bd=1, width=7)
        # green if POS device connected to server
        self.server_indicator = StatusIndicator(self,  "Server", bd=1, width=7)
        # green if Display device connected to server
        self.display_indicator = StatusIndicator(self, "Display", bd=1, width=7)
        
        grid_kwargs = {"sticky":"nsw",
                        "padx": 2}
        self.network_indicator.grid(row=0, column=0, **grid_kwargs)
        self.server_indicator.grid(row=0, column=1, **grid_kwargs)
        self.display_indicator.grid(row=0, column=2, **grid_kwargs)
        self.get_connection_status()

        
    
    @update
    def get_connection_status(self):
        AsyncTk().forward("get_connection_status", 
                self.network_indicator,
                self.server_indicator,
                self.display_indicator)


@lib.log_info("Global shutdown in 5", time=True)
def shutdown():
    async def _():
        counter = 5
        while counter > 0:
            lib.stdout.write(f"{counter}s", replace=3)
            await asyncio.sleep(1)
            counter -= 1
        lib.AsyncTk().destroy()
        lib.AsyncTk().forward("global_shutdown")
    lib.AsyncTk().add_task(_())

@lib.log_info("Program restart in 5", time=True)
def reboot():
    async def _():
        counter = 5
        while counter > 0:
            lib.stdout.write(f"{counter}s", replace=3)
            await asyncio.sleep(1)
            counter -= 1
        main = sys.executable
        os.execl(main, main, *sys.argv)
    lib.AsyncTk().add_task(_())

class ShutdownButton(lib.LabelButton, metaclass=lib.WidgetType, device="POS"):
    font = ("Courier", 10)
    
    class shutdown_callback(tk.Toplevel, metaclass=lib.WidgetType, device="POS"):
        font=("Courier", 12)

        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.title("Shutdown")
            label = tk.Label(self, text="Shutdown Options", font=self.font)
            shutdown_button = lib.LabelButton(self, "Shutdown", font=self.font, bg="red", command=partial(shutdown))
            restart_button = lib.LabelButton(self, "Restart", font=self.font, bg="red", command=partial(reboot))
            close_button = lib.LabelButton(self, "Close", font=self.font, bg="green", command=partial(self.destroy))
            label.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, ipady=5)
            shutdown_button.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)
            restart_button.grid(row=2, column=1, sticky="nswe", padx=5, pady=5)
            close_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, "Shutdown",
                font=self.font,
                command=partial(self.shutdown_callback, self), **kwargs)
        
class Clock(tk.Entry, metaclass=lib.WidgetType, device="POS"):

    font = ("Courier", 12)

    def __init__(self, parent, **kwargs):
        super().__init__(parent,
            width=11,
            font=self.font,
            state=tk.DISABLED,
            disabledbackground="white",
            disabledforeground="black",
            relief=tk.RIDGE, **kwargs)
        self._time = tk.StringVar(self)
        self["textvariable"] = self._time
        lib.AsyncTk().add_task(self.update_time())
    
    async def update_time(self):
        while True:
            self._time.set(strftime("%I:%M:%S %p", localtime()))
            await asyncio.sleep(1)

def titlebar(parent, **kwargs):
    frame = tk.Frame(parent, **kwargs)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    frame.grid_columnconfigure(2, weight=1)

    network_status = NetworkStatus(frame, relief=tk.RIDGE, bd=2)
    network_status.grid(row=0, column=0, sticky="w")
    clock = Clock(frame)
    clock.grid(row=0, column=1, pady=2, padx=2, sticky="we")
    shutdown_button = ShutdownButton(frame, bg="red")
    shutdown_button.grid(row=0, column=2, sticky="e")
    return frame