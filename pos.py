from lib import AsyncTk
from POS import NetworkStatus
from POS import OrderDisplay
from POS import MenuDisplay
from POS import ShutdownButton
from POS import titlebar
from POS import Console
from POS import PriceDisplay
from POS import MenuEditor
import tkinter as tk
import logging
from mem_top import mem_top

def main(protocol):
    main = AsyncTk(protocol())
    main.geometry("1280x800")
    main.grid_columnconfigure(2, weight=2)
    main.grid_rowconfigure(1, weight=1)
    main.resizable(False, False)
    title_bar = titlebar(main, bd=2)
    menu_display = MenuDisplay(main, relief=tk.RIDGE, bd=2)
    order_display = OrderDisplay(main, bd=2, relief=tk.RIDGE)
    editor = MenuEditor(main, bd=2, relief=tk.RIDGE)

    console = Console(main, bd=2, relief=tk.RIDGE)
    price_display = PriceDisplay(main, relief=tk.RIDGE, bd=2)

    title_bar.grid(row=0, column=0, columnspan=3, sticky="nswe", padx=2, pady=2)
    menu_display.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=2, pady=2)
    editor.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=2, pady=2)
    menu_display.lift()
    order_display.grid(row=1, column=2, pady=2, padx=2, sticky="nswe")
    console.grid(row=2, column=0,  columnspan=2, pady=5, sticky="nswe")
    price_display.grid(row=2, column=2)


    # add methods to tkinter's update loop
    price_display.update()
    

    main()