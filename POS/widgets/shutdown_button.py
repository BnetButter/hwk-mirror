import tkinter as tk
import sys
import os
from lib import LabelButton
from lib import AsyncTk
from lib import WidgetType
from functools import partial
from lib import log_info
from lib import stdout
import asyncio

@log_info("Global shutdown in 5", time=True)
def shutdown():
    async def _():
        counter = 5
        while counter > 0:
            stdout.write(f"{counter}s", replace=3)
            await asyncio.sleep(1)
            counter -= 1
        AsyncTk().destroy()
        AsyncTk().forward("global_shutdown")
    AsyncTk().add_task(_())

@log_info("Program restart in 5", time=True)
def reboot():
    async def _():
        counter = 5
        while counter > 0:
            stdout.write(f"{counter}s", replace=3)
            await asyncio.sleep(1)
            counter -= 1
        main = sys.executable
        os.execl(main, main, *sys.argv)
    AsyncTk().add_task(_())

class ShutdownButton(LabelButton, metaclass=WidgetType, device="POS"):
    font = ("Courier", 10)
    
    class shutdown_callback(tk.Toplevel, metaclass=WidgetType, device="POS"):
        font=("Courier", 12)

        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.title("Shutdown")
            label = tk.Label(self, text="Shutdown Options", font=self.font)
            shutdown_button = LabelButton(self, "Shutdown", font=self.font, bg="red", command=partial(shutdown))
            restart_button = LabelButton(self, "Restart", font=self.font, bg="red", command=partial(reboot))
            close_button = LabelButton(self, "Close", font=self.font, bg="green", command=partial(self.destroy))
            label.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, ipady=5)
            shutdown_button.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)
            restart_button.grid(row=2, column=1, sticky="nswe", padx=5, pady=5)
            close_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, "Shutdown",
                font=self.font,
                command=partial(self.shutdown_callback, self), **kwargs)
        

