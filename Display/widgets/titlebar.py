import tkinter as tk
import lib

class NetworkStatus(tk.Frame):

    def __init__(self, parent, font=None, **kwargs):
        super().__init__(parent, **kwargs)
        # green if device connected to network
        self.network_indicator = lib.StatusIndicator(self, 
                "Network", bd=1, width=7, font=font)
        # green if device connected to server
        self.server_indicator = lib.StatusIndicator(self, 
                "Server", bd=1, width=7, font=font)
        # green if POS device connected to server
        self.pos_indicator = lib.StatusIndicator(self, 
                "POS", bd=1, width=7, font=font)
        


        grid_kwargs = {"sticky":"nsw",
                        "padx": 2, "pady":2}
        self.network_indicator.grid(row=0, column=0, **grid_kwargs)
        self.server_indicator.grid(row=0, column=1, **grid_kwargs)
        self.pos_indicator.grid(row=0, column=2, **grid_kwargs)
 
    @lib.update
    def update(self):
        network, server, client = lib.AsyncTk().forward("get_connection_status")
        self.network_indicator.set(network)
        self.server_indicator.set(server)
        if client is None:
            client = False
        else:
            client = "POS" in client
        self.pos_indicator.set(client)


class TitleBar(tk.Frame, metaclass=lib.WidgetType, device="Display"):
    font = ("Courier", 16)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        

        self.network_status = NetworkStatus(self, relief=tk.RIDGE, bd=2, font=self.font)
        self.network_status.grid(row=0, column=0, sticky="w", pady=5, padx=2)
        self.clock = lib.Clock(self, font=self.font)
        self.clock.grid(row=0, column=1, sticky="w", padx=5)
 
    def update(self):
        lib.AsyncTk().add_task(self.clock.update())
        self.network_status.update()
