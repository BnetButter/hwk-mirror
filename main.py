import logging
import sys
from lib import AsyncWindow
from POS import MenuDisplay
from POS import OrderDisplay
from POS import Console
from POS import PriceDisplay
from POS import NetworkStatus
from POS import ShutdownButton
from POS import server


from collections import UserList
import lib.tkwidgets
import lib
from tkinter import ttk
import tkinter as tk
from io import StringIO
import asyncio
from lib import Event

main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
main_stdout = logging.StreamHandler(stream=sys.stdout)
main_logger.addHandler(main_stdout)

from functools import partial

def pos():

    main = AsyncWindow(className="POS")
    main.geometry("1280x800")
    main.grid_columnconfigure(1, weight=2)
    
    main.grid_rowconfigure(1, weight=1)
    main.resizable(False, False)

    Event(print=lambda message: print(message))
    
    network_status = NetworkStatus(main, bd=2)    
    shutdown_button = ShutdownButton(main, bg="red")

    menu_display = MenuDisplay(main, relief=tk.RIDGE, bd=2)
    
    order_display = OrderDisplay(main, bd=2, relief=tk.RIDGE)
    console = Console(main, bd=2, relief=tk.RIDGE)

    network_status.grid(row=0, column=0, sticky="w", padx=2)
    shutdown_button.grid(row=0, column=1, sticky="e", padx=4)
    menu_display.grid(row=1, column=0, sticky="nswe", padx=2, pady=2)
    order_display.grid(row=1, column=1, pady=2, padx=2, sticky="nswe")
    console.grid(row=2, column=0, pady=5, sticky="nswe")
    price_display = PriceDisplay(main, relief=tk.RIDGE, bd=2)
    price_display.grid(row=2, column=1)
    main.mainloop()

def server_init():
    from time import localtime    
    main = AsyncWindow(className="Server")
    current_time = server.ServerFrame(main)
    current_time.grid(row=0, column=0, sticky="nswe")
    main.mainloop()

server_init()

