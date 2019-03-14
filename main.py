import logging
import sys

main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
main_stdout = logging.StreamHandler(stream=sys.stdout)
main_logger.addHandler(main_stdout)



if __name__ == "__main__":
    from lib import AsyncWindow
    from POS import MenuDisplay
    from POS import OrderDisplay
    from POS import Console
    from POS import PriceDisplay
    import lib
    
    from tkinter import ttk
    import tkinter as tk

    main = AsyncWindow()
    main.geometry("1280x800")
    main.grid_columnconfigure(1, weight=2)
    main.grid_rowconfigure(0, weight=1)
    main.resizable(False, False)

    menu_display = MenuDisplay(main, relief=tk.RIDGE, bd=2)
    menu_display.grid(row=0, column=0, sticky="nswe", padx=2, pady=2)
    
    order_display = OrderDisplay(main, bd=2, relief=tk.RIDGE)
    order_display.grid(row=0, column=1, pady=2, padx=2, sticky="nswe")

    console = Console(main, bd=2)
    console.grid(row=2, column=0, pady=5, sticky="nswe")

    price_display = PriceDisplay(main, relief=tk.RIDGE, bd=2)
    price_display.grid(row=2, column=1)

    main.mainloop()








