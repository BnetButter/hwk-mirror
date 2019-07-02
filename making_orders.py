"""Shows how OrderDisplay and OrderDisplay widgets interact"""
import lib
import POS
import tkinter as tk


if __name__ == "__main__":
    
    app = lib.AsyncTk(POS.POSProtocol())
    app.geometry("1280x700")
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    menu_display = POS.MenuDisplay(app)
    order_display = POS.OrderDisplay(app)
    order_display.grid(row=0, column=1, sticky="nswe")
    menu_display.grid(row=0, column=0, sticky="nswe")
    app.mainloop()
