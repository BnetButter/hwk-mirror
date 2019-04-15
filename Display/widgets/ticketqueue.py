from .ticketbox import TicketInfoFrame

import tkinter as tk
import lib

class TicketQueue(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.show_num = lib.AsyncTk().forward("show_num_tickets")
        self.widgets = [TicketInfoFrame(self) for i in range(self.show_num)]
        self.bind("<KP_Enter>", self.advance)

    @lib.update
    def update(self):
        num = 0
        for i, ticket in enumerate(lib.AsyncTk().forward("tickets")):
            if i < self.show_num:
                self.widgets[i].update(ticket)
                self.widgets[i].pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
                num = i + 1
        
        for widget in self.widgets[num: ]:
            widget.pack_forget()

    def advance(self, *args):        
        completed = self.widgets[0].ticket
        # no ticket showed on screen. nothing to do
        if completed is None:
            return        
        lib.AsyncTk().forward("set_ticket_status", 
                completed.index, 
                lib.TICKET_COMPLETE)

    def test_button(self):
        button = tk.Button(self, text="test queue_advance")
        button["command"] = self.advance
        return button