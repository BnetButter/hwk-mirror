import tkinter as tk
import collections
import time
import asyncio
import operator
import lib

# doesn't actually move. but looks like it does
class ScrollingUpdate(collections.UserList, metaclass=lib.SingletonType):

    def __init__(self, master=None, initlist=None, orient=tk.HORIZONTAL, reverse=False):
        super().__init__(initlist)
        self.offset = 0
        self.show = 5 if initlist is None else len(initlist)
        self.last_list_len = None
        self._reverse = reverse
        if reverse:
           self.skip = -1
        else:
            self.skip = 1

        if orient == tk.HORIZONTAL:
            master.bind_all("<KP_Left>", self.inc_offset if reverse else self.dec_offset)
            master.bind_all("<KP_Right>", self.dec_offset if reverse else self.inc_offset)

        elif orient == tk.VERTICAL:
            master.bind_all("<KP_Up>", self.inc_offset if reverse else self.dec_offset)
            master.bind_all("<KP_Down>", self.dec_offset if reverse else self.inc_offset)
        else:
            raise ValueError
        self.orient = orient
    
    def advance(self):
        if self._reverse:
            self.inc_offset()
        else:
            self.dec_offset()
    
    def get(self):
        if self._reverse:
            return self[-1].get()
        else:
            return self[0].get()

    def inc_offset(self, *event):
        self.offset += 1

    def dec_offset(self, *event):
        if self.offset - 1 >= 0:
            self.offset -= 1
    
    def update(self, lst):
        if self.last_list_len is None:
            self.last_list_len = len(lst)
        lst_len = len(lst)
        self_len = len(self)
        if not lst:
            self.offset = 0

        if lst_len < self.last_list_len and self.offset:
            diff = self.last_list_len - lst_len
            if self.offset - diff >= 0:
                self.offset -= diff
            else:
                self.offset = 0


        if self.offset + self.show > lst_len:
            self.offset -= 1
            
        if self_len > lst_len + self.offset:
            self.offset = 0
            for widget in self:
                widget.reset()

        for widget, obj in zip(self[::self.skip], lst[self.offset:]):
            widget.update(obj)
        
        self.last_list_len = lst_len
        
        if self._reverse:
            if lst_len:
                lo = self.offset / lst_len
                hi = (self.show / lst_len) + lo
                return 1 - hi, 1 -lo
            else:
                return 0, 1
        else:
            if lst_len:
                lo = self.offset / lst_len
                hi = (self.show / lst_len) + lo
                return lo, hi
            else:
                return 0,1


class DiscreteScrolledFrame(tk.Frame):

    def __init__(self, master, initwidget, nmemb, orient=tk.HORIZONTAL, reverse=False, **kwargs):
        assert callable(initwidget)
        super().__init__(master, **kwargs)
        self._interior = tk.Frame(self)
        self.scroller = ScrollingUpdate(self,
                initlist=[initwidget(master=self._interior) for i in range(nmemb)],
                orient=orient,
                reverse=reverse)
        self.scrollbar = tk.Scrollbar(self, orient=orient)
        if orient == tk.HORIZONTAL:
            self.grid_columnconfigure(0, weight=1)
            self._interior.grid(row=0, column=0, sticky="nswe")
            self.scrollbar.grid(row=1, column=0, sticky="nswe")
        elif orient == tk.VERTICAL:
            self.grid_rowconfigure(0, weight=1)
            self._interior.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.orient = orient

    def update(self, synclist):
        self.data = synclist
        self.scrollbar.set(*self.scroller.update(synclist))

    def grid_inner(self, **kwargs):
        if self.orient == tk.HORIZONTAL:
            self._interior.grid_rowconfigure(0, weight=1)
            for i, widget in enumerate(self.scroller):
                self._interior.grid_columnconfigure(i, weight=1)
                widget.grid(row=0, column=i, **kwargs)
            if self.scroller._reverse:
                self._interior.grid_columnconfigure(len(self.scroller)-1, weight=0)
            else:
                self._interior.grid_columnconfigure(0, weight=0)
        elif self.orient == tk.VERTICAL:
            self._interior.grid_columnconfigure(0, weight=1)
            for i, widget in enumerate(self.scroller):
                self._interior.grid_rowconfigure(i, weight=2)
                widget.grid(row=i, column=0, **kwargs)
            # widgets that are first must fully expand
            if self.scroller._reverse:
                self._interior.grid_rowconfigure(len(self.scroller)-1, weight=0)
            else:
                self._interior.grid_rowconfigure(0, weight=0)

