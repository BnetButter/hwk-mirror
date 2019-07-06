from .scroll import DiscreteScrolledFrame
from LineDisplay.line_protocol import TicketData
import tkinter as tk
import lib

class ItemInfo(tk.Frame):
    font=("Courier", 30)

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="grey16", **kwargs)
        bg = "grey16"
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.item_label = tk.Label(self, 
                fg="white",
                bg=bg, width=24,
                font=self.font,
                bd=2,
                justify=tk.LEFT,
                anchor=tk.NW)
        self.options_label = tk.Label(self,
                fg="white",
                bg=bg,
                width=24,
                font=("Courier", 20),
                justify=tk.LEFT,
                anchor=tk.NW)
        self.comments_label = tk.Label(self,
                fg="white",width=24,bg=bg,
                font=("Courier", 20, "italic"),
                justify=tk.LEFT,
                anchor=tk.NW)
        self.item_label.grid(
                row=0,
                column=0,
                sticky="nswe")
        self.options_label.grid(
                row=1,
                column=0,
                sticky="we")
        self.comments_label.grid(
                row=2,
                column=0,
                sticky="nwe")

        self.pad = tk.Label(self, font=("Courier", 20, "italic"),
                bg=bg)
        self.pad.grid(row=3, column=0, sticky="nwe") 

    def reset(self):
        self.item_label["text"] = ""
        self.options_label["text"] = ""
        self.comments_label["text"] = ""
        self.set_bg("grey16")

    def set_bg(self, bg):
        self.item_label["bg"] = bg
        self.options_label["bg"] = bg
        self.comments_label["bg"] = bg
        self.pad["bg"] = bg
        self["bg"] = bg


    def update(self, ticket):
        if not ticket:
            return self.reset()
        self.item_label["text"] = ticket.name
        options = "\n".join("  + " + option for option in ticket.selected_options)
        if ticket.selected_options:
            self.options_label["text"] = options
            self.options_label.grid()
        else:
            self.options_label.grid_remove()
        comments = ticket.parameters.get("comments", False)
        if comments:
            self.comments_label["text"] = "    " + comments
            self.comments_label.grid()
        else:
            self.comments_label.grid_remove()
            
        if ticket.parameters.get("status") == lib.TICKET_COMPLETE:
            self.set_bg("green")
        else:
            self.set_bg("grey16")
        


class TicketInfo(tk.Frame):

    def __init__(self, master, ncol, **kwargs):
        super().__init__(master, bd=3, bg="grey16", **kwargs)
        for i in range(ncol):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.widgets = [ItemInfo(self, relief=tk.GROOVE, bd=2) for i in range(ncol)]
        self.ncol = ncol
        
        for i, widget in enumerate(self.widgets):
            widget.grid(row=0, column=i, sticky="nswe")
        self.ticket_no = tk.Label(self, bg="grey16", fg="white", relief=tk.RIDGE, font=("Courier", 20))
        self.ticket_no.grid(row=0, column=0, sticky="sw")
        self.data = None

    def update(self, data):
        self.data = data
        for widget in self.widgets:
            widget.reset()
        for subindex, item in enumerate(data.all()):
            self.widgets[subindex].update(item)
        if data:
            self.ticket_no.grid()
            self.ticket_no["text"] = "{:03d}: {}".format(data.ticket_no, data.name)\
                     if data.name else "{:03d}".format(data.ticket_no)
            
            if data.deliver:
                self.ticket_no["bg"] = "red"
                self["bg"] = "red"
            else:
                self.ticket_no["bg"] = "grey16"
                self["bg"] = "grey16"
            
        else:
            self.reset()
            
    def reset(self):
        for item in self.widgets:
            item.reset()
        self.ticket_no.grid_remove()
        self["bg"] = "grey16"
    
    def get(self):
        return self.data
    

                


class TicketQueue(DiscreteScrolledFrame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        for i in range(len(self.scroller)):
            self.grid_rowconfigure(i, weight=1)
        self.grid_inner()
    
    @lib.update
    def update(self):
        super().update(lib.AsyncTk().forward("tickets"))
  
    def on_enter(self, event):
        lib.AsyncTk().forward(
                "set_item_status",
                self.scroller.get(),
                lib.TICKET_COMPLETE)

    def recenter(self, *args):
        self.scroller.offset = 0
        super().update(lib.AsyncTk().forward("tickets"))
        while True:
            if any(item.parameters.get("status") == lib.TICKET_COMPLETE for item in self.scroller.get()):
                self.scroller.advance()
                super().update(lib.AsyncTk().forward("tickets"))
                continue
            return
    
    