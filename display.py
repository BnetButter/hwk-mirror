# shows orders on drinks line
import LineDisplay
import lib
import tkinter as tk
import sys
import subprocess
import functools

def main(protocol, ncol, geometry=None):
    app = lib.AsyncTk(protocol())
    if lib.DEBUG:
        fullscreen = False
        assert geometry is not None
    else:
        fullscreen = True
        geometry = f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}"
        # set baudrate for printer
        subprocess.call("stty -F /dev/serial0 19200", shell=True)
    
    app.attributes("-fullscreen", fullscreen)
    app.geometry(geometry)
    app.resizable(False, False)    
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    queue = LineDisplay.TicketQueue(
            app,
            functools.partial(
                LineDisplay.TicketInfo,
                ncol=ncol),
            5,
            orient=tk.VERTICAL,
            reverse=True)
    titlebar = LineDisplay.TitleBar(app, bg="grey16")
    queue.grid(row=0, column=0, sticky="nswe")
    queue.grid_inner(columnspan=2, sticky="nswe")
    titlebar.grid(row=1, column=0, sticky="we")
    queue.update()
    titlebar.update()
    app.bind("<KP_Enter>", queue.on_enter)
    app.bind("<KP_0>", titlebar.toggle_print)
    app.bind("<KP_Insert>", titlebar.toggle_print)

    app.bind("<KP_Begin>", queue.recenter)
    app.bind("<KP_5>", queue.recenter)

    app.mainloop()
    