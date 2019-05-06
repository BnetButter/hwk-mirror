#! /home/pi/.local/bin/python3.7

import lib
import Display
import tkinter as tk
import logging
import sys

def main(delegate):
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(name)s - %(message)s"))
    logger.addHandler(handler)

    main = lib.AsyncTk(delegate())
    main.geometry("1080x1920+1920+0")
    main.resizable(False, False)
    main.attributes("-fullscreen", True)

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