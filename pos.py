from lib import AsyncTk
import POS
import tkinter as tk
import logging
import sys


def main(protocol):

    logger = logging.getLogger("main.POS")
    logger.setLevel(logging.INFO)
    
    main = AsyncTk(protocol())
    main.geometry("1280x800")
    main.grid_columnconfigure(2, weight=2)
    main.grid_rowconfigure(1, weight=1)
    main.resizable(False, False)
    
    title_bar = POS.TitleBar(main, bd=2)
    menu_display = POS.MenuDisplay(main, relief=tk.RIDGE, bd=2)
    order_display = POS.OrderDisplay(main, bd=2, relief=tk.RIDGE)
    editor = POS.MenuEditor(main, bd=2, relief=tk.RIDGE)
    console = POS.Console(main, bd=2, relief=tk.RIDGE)
    price_display = POS.PriceDisplay(main, relief=tk.RIDGE, bd=2)

    title_bar.grid(row=0, column=0, columnspan=3, sticky="nswe", padx=2, pady=2)
    menu_display.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=2, pady=2)
    editor.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=2, pady=2)
    menu_display.lift()
    order_display.grid(row=1, column=2, pady=2, padx=2, sticky="nswe")
    console.grid(row=2, column=0,  columnspan=2, pady=5, sticky="nswe")
    price_display.grid(row=2, column=2)

    # add methods to tkinter's update loop
    order_display.update()
    editor.update()
    price_display.update()
    title_bar.update()

    # add shutdown task
    protocol.shutdown(main.delegate, cleanup=AsyncTk().destroy)
    main.mainloop()