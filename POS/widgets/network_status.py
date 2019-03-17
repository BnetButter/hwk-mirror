import tkinter as tk
import lib

class StatusIndicator(lib.ToggleSwitch, metaclass=lib.WidgetType, device="POS"):
    font=("Courier", 10)
    
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, text,
                config_true={"relief": tk.SUNKEN,"bg":"green3"},
                config_false={"relief": tk.RAISED, "bg":"red"},
                font=self.font)
        self.state=False
        # disable user control
        

class NetworkStatus(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # green if POS device connected to network
        self.network_indicator = StatusIndicator(self, "Network", bd=1, width=7)
        # green if POS device connected to server
        self.server_indicator = StatusIndicator(self,  "Server", bd=1, width=7)
        # green if Display device connected to server
        self.display_indicator = StatusIndicator(self, "Display", bd=1, width=7)

        grid_kwargs = {"sticky":"nsw",
                        "padx": 2}
        self.network_indicator.grid(row=0, column=0, **grid_kwargs)
        self.server_indicator.grid(row=0, column=1, **grid_kwargs)
        self.display_indicator.grid(row=0, column=2, **grid_kwargs)