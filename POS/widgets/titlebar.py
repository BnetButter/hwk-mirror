from functools import partial
from time import strftime, localtime
from lib import AsyncTk, update
import lib
import asyncio
import lib
import tkinter as tk
import sys
import os

class NetworkStatus(tk.Frame):

    def __init__(self, parent, font=None, **kwargs):
        super().__init__(parent, **kwargs)
        # green if POS device connected to network
        self.network_indicator = lib.StatusIndicator(self, "Network", bd=1, width=7, font=font)
        # green if POS device connected to server
        self.server_indicator = lib.StatusIndicator(self,  "Server", bd=1, width=7, font=font)
        # green if Display device connected to server
        self.display_indicator = lib.StatusIndicator(self, "Display", bd=1, width=7, font=font)
        
        grid_kwargs = {"sticky":"nsw",
                        "padx": 2, "pady":2}
        self.network_indicator.grid(row=0, column=0, **grid_kwargs)
        self.server_indicator.grid(row=0, column=1, **grid_kwargs)
        self.display_indicator.grid(row=0, column=2, **grid_kwargs)
 
    @update
    def update(self):
        network, server, client = AsyncTk().forward("get_connection_status")
        self.network_indicator.set(network)
        self.server_indicator.set(server)
        if client is None:
            client = False
        else:
            client = "Display" in client
        self.display_indicator.set(client)

def shutdown():
    async def _():
        counter = 5
        lib.stdout.write(f"Global shutdown in {counter}s")
        lib.AsyncTk().forward("global_shutdown", counter)
        lib.AsyncTk().forward("print_daily_sales")
        while counter > 0:
            lib.stdout.write(f"{counter}s", replace=3)
            await asyncio.sleep(1)
            counter -= 1
    lib.AsyncTk().add_task(_())

def reboot():
    async def _():
        counter = 5
        lib.stdout.write(f"Restart in {counter}s")
        while counter > 0:
            lib.stdout.write(f"{counter}s", replace=3)
            await asyncio.sleep(1)
            counter -= 1
        lib.AsyncTk().destroy(shutdown=False)
        await asyncio.sleep(1)
        main = sys.executable
        os.execl(main, main, *sys.argv)
    lib.AsyncTk().add_task(_())

class ShutdownButton(lib.LabelButton, metaclass=lib.WidgetType, device="POS"):
    font = ("Courier", 10)
    
    class shutdown_callback(tk.Toplevel, metaclass=lib.ToplevelWidget, device="POS"):
        font=("Courier", 12)

        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.title("Shutdown")
            label = tk.Label(self, text="Shutdown Options", font=self.font)
            shutdown_button = lib.LabelButton(self, "Shutdown", font=self.font, bg="red", command=partial(shutdown))
            restart_button = lib.LabelButton(self, "Restart", font=self.font, command=partial(reboot))
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

class TitleBar(tk.Frame, metaclass=lib.WidgetType, device="POS"):
    font = ("Courier", 12)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.network_status = NetworkStatus(self, relief=tk.RIDGE, bd=2)
        self.network_status.grid(row=0, column=0, sticky="w")
        self.clock = lib.Clock(self, font=self.font)
        self.clock.grid(row=0, column=1, sticky="we")
        self.shutdown_button = ShutdownButton(self, bg="red")
        self.shutdown_button.grid(row=0, column=2, sticky="e")

    def update(self):
        AsyncTk().add_task(self.clock.update())
        self.network_status.update()