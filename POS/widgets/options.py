from tkinter import ttk
import tkinter as tk
import lib
import functools



class EditOptionsFrame(tk.Frame, metaclass=lib.WidgetType, device="POS"):
    font=("Courier", 16)
    def __init__(self, parent, item, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        label = tk.Label(self, font=self.font, text=f"{item.name}", width=25, justify=tk.LEFT, anchor=tk.NW)
        self.ticket = item
        self.options = [lib.ToggleSwitch(self, text=option, font=self.font, width=15) for option in item.options]
        self._comments = tk.StringVar(self)
        comment = item.parameters.get("comments", "")
        self._comments.set(comment if comment else "Comments")
        self.comments = tk.Entry(self, textvariable=self._comments, font=self.font)
        self.grid_columnconfigure(0, weight=1)

        label.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        tk.Label(self, text="    ", font=self.font).grid(row=1, column=0, sticky="nswe")
        for i, option in enumerate(self.options):
            if option["text"] in item.selected_options:
                option.state = True
            option.grid(row=i+1, column=1, sticky="nwe", padx=5, pady=5)
        
        self.grid_rowconfigure(len(self.options) + 2, weight=1)
        self.comments.grid(row=len(self.options) + 2, column=0, columnspan=2, pady=5, padx=5, sticky="swe")
        self.comments.bind("<FocusIn>", self.on_entry_focus)

    def apply(self):
        self.ticket.selected_options = (option["text"] for option in self.options if option)
        self.ticket.parameters["comments"] = self._comments.get().replace("Comments", "")

    def on_entry_focus(self, event):
        if "Comments" in self._comments.get():
            self._comments.set("")


class EditOptions(tk.Toplevel, metaclass=lib.ToplevelWidget, device="POS"):
    font = ("Courier", 16, "bold")

    def __new__(cls, parent, ticket, *args, **kwargs):
        if ticket.name:
            return super().__new__(cls)
        
    def __init__(self, parent, ticket, *args, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self._frame = EditOptionsFrame(self, ticket)
        self._frame.grid(row=0, column=0, sticky="nswe", columnspan=2)
        done = tk.Button(self, text="Done", bg="green", command=self.destroy)
        close = tk.Button(self, text="Close", bg="red", command=super().destroy) # doesn't save
        done.grid(row=1, column=1, pady=10, padx=5, sticky="nswe")
        close.grid(row=1, column=0, pady=10, padx=5, sticky="nswe")

    def destroy(self, *args):
        self._frame.apply()
        super().destroy()

    @classmethod
    def call(cls, parent, ticket):
        return functools.partial(cls, parent, ticket)


class GroupEditOptions(tk.Toplevel, metaclass=lib.ToplevelWidget, device="POS"):
    font=()

    def __new__(cls, master, ticket, **kwargs):
        if ticket.options and ticket.addon1.options and ticket.addon2.options:
            return super().__new__(cls, master, ticket, **kwargs)

    def __init__(self, master, ticket, **kwargs):
        super().__init__(master, **kwargs)
        self.editors = []
        last_sep = None  
        generator = (ticket for ticket in (ticket, ticket.addon1, ticket.addon2) if ticket.name)
        bt_frame = tk.Frame(self, bd=2, relief=tk.GROOVE, padx=10)
        bt_frame.grid(row=1, column=0, columnspan=6, sticky="nswe")
        bt_frame.grid_columnconfigure(1, weight=1)
        for i, item in enumerate(generator):
            if item.options:
                self.grid_columnconfigure(i * 2, weight=1)
                editor = EditOptionsFrame(self, item)
                editor.grid(row=0, column=(i * 2), sticky="nswe")
                self.editors.append(editor)
                last_sep = ttk.Separator(self, orient=tk.VERTICAL)
                last_sep.grid(row=0, column=(i * 2) + 1, sticky="ns")
        if last_sep is not None:
            last_sep.grid_remove()
        
        done = tk.Button(bt_frame, text="Done", width=8, bg="green", command=self.destroy)
        close = tk.Button(bt_frame, text="Close", width=8, bg="red", command=super().destroy) # doesn't save
        done.grid(row=0, column=2, pady=10, padx=5, sticky="nse")
        close.grid(row=0, column=1, pady=10, padx=5, sticky="nse")

    def destroy(self, *args):
        for editor in self.editors:
            editor.apply()
        super().destroy()