import POS
import Server
import functools
import tkinter as tk
import multiprocessing
import pos
import server

if __name__ == "__main__":
    pos = multiprocessing.Process(target=pos.main, args=(POS.POSProtocol,))
    server = multiprocessing.Process(target=server.main)
    # devices are offline so need to set time manually
    Server.ServerTimeApp().mainloop()
    server.start()
    pos.start()