from tkinter import ttk
import tkinter as tk
import lib


class TicketInfo(tk.Frame, metaclass=lib.WidgetType, device="Display"):
    font = ("Courier", 20, "bold")
    comment_font = ("Courier", 16, "italic")
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                bd=7,
                bg="white smoke",
                **kwargs)

        tk.Frame(self,width=340,
                height=340).grid(sticky="nswe")
        self.info_label = tk.Message(self,
                font=self.font,
                anchor=tk.CENTER,
                bg="white smoke",
                width=1000)
        self.comments = tk.Label(self, 
                justify=tk.LEFT,
                font=self.comment_font,
                width=20,
                bg="white smoke")

        self.info_label.grid(row=0, column=0, sticky="nswe")
        self.comments.grid(row=1, column=0, sticky="nse")
        self.ticket = None
    
    def reset(self):
        self["bg"] = "white smoke"
        self.info_label["bg"] = "white smoke"
        self.info_label["text"] = ""

    def mark_complete(self):
        self["bg"] = "green"
        self.info_label["bg"] = "grey26"

    def disable(self):
        self.info_label["text"] = "(null)"

    def update(self, ticket):
        self.ticket = ticket
        status = ticket.parameters.get("status")

        if status == lib.TICKET_WORKING:
            if ticket.parameters.get("register", False):
                self.info_label["bg"] = "grey"
                self["bg"] = "green"
            else:
                self.info_label["bg"] = "yellow"
                self["bg"] = "yellow"
        
        elif status == lib.TICKET_COMPLETE: # shouldn't happen
            self["bg"] = "grey"
            self.info_label["bg"] = "grey"
            self.comments["bg"] = "grey"
        
        else:
            self.comments["bg"] = "white smoke"
            self.info_label["bg"] = "white smoke"
            self["bg"] = "white smoke"

        text = "\n".join((f"    + {option}" 
                    for option in ticket.selected_options))
        if text:
            text = ticket.name + "\n" + text
        else:
            text = ticket.name
        self.info_label["text"] = text
        self.comments["text"] = ticket.parameters.get("comments", "")


class TicketInfoFrame(tk.Frame, metaclass=lib.WidgetType, device="Display"):
    font = ("Courier", 20)
    null_ticket = lib.NULL_TICKET_ITEM

    def __init__(self, parent, **kwargs):
        super().__init__(parent, 
                bd=2,bg="white smoke",
                **kwargs)
        self.ticket = None
        self.ticket_no = tk.Label(self, 
                font=self.font, 
                padx=5,
                bd=2,
                bg="white smoke")
        self.deliver = tk.Label(self,
                font=self.font,
                bg="red",
                text="Deliver")
        self.item_info = TicketInfo(self)
        self.addon1_info = TicketInfo(self)
        self.addon2_info = TicketInfo(self)

        for i in range(3):
            self.grid_columnconfigure(i,weight=1)
        self.item_info.grid(row=0, column=0, sticky="nswe", ipadx=2)
        self.addon1_info.grid(row=0, column=1, sticky="nswe", ipadx=2)
        self.addon2_info.grid(row=0, column=2, sticky="nswe", ipadx=2)
        self.deliver.grid(row=0, column=0, sticky="nw")
        self.deliver.grid_remove()
        self.ticket_no.grid(row=0, column=0, sticky="ws")
        self.ticket_no.lift()
    
    def reset(self):
        self.item_info.reset()
        self.addon1_info.reset()
        self.addon2_info.reset()
        self.ticket_no["relief"] = tk.FLAT
        self["relief"] = tk.FLAT

    def update(self, ticket):
        order_queue = lib.AsyncTk().forward("order_queue")
        name = order_queue[str(ticket.ticket_no)]["name"]
        deliver = order_queue[str(ticket.ticket_no)]["deliver"]
        if not ticket:
            return self.reset()
        self.ticket = ticket
        self["relief"] = tk.RIDGE
        self.ticket_no["relief"] = tk.RAISED
        
        text = "{:03d}".format(ticket.ticket_no)
        if name:
            text += f": {name}"
        self.ticket_no["text"] = text
        self.item_info.update(ticket)
        self.addon1_info.update(ticket.addon1)
        self.addon2_info.update(ticket.addon2)

        if deliver:
            self.deliver.grid()
            self.deliver.lift()
            self["bg"] = "red"
            self.ticket_no["bg"] = "red"
        else:
            self.deliver.grid_remove()
            self["bg"] = "white smoke"
            self.ticket_no["bg"] = "white smoke"