#! /home/pi/.local/bin/python3.7

import lib
import Display
import tkinter as tk
import logging
import sys
import subprocess

def main(delegate):
    logger = logging.getLogger("main")
    main = lib.AsyncTk(delegate())
    if lib.DEBUG:
        geometry = "1920x1080+1920+0"
        fullscreen = False
    else:
        geometry = "1080x1920"
        fullscreen = True
        # set baudrate for receipt printer
        subprocess.call("stty -F /dev/serial0 19200", shell=True)  
    main.attributes("-fullscreen", fullscreen)
    main.geometry(geometry)
    main.resizable(False, False)
    
    title_bar = Display.TitleBar(main)
    ticket_queue = Display.TicketQueue(main)

    main.bind_all("<KP_Enter>", ticket_queue.advance)
    main.bind_all("<Return>", ticket_queue.advance)

    title_bar.pack(fill=tk.X, side=tk.BOTTOM)
    ticket_queue.pack(fill=tk.BOTH, side=tk.BOTTOM)
    
    # add update task to mainloop
    title_bar.update()
    ticket_queue.update()
    # add update task to async tasks
    delegate.shutdown(main.delegate, cleanup=lib.AsyncTk().destroy)
    main.mainloop()
