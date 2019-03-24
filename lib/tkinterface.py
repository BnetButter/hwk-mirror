from functools import wraps
from functools import partial
from operator import itemgetter
from .data import GUI_STDERR
from .data import GUI_STDOUT
from .data import log_info
import asyncio
import tkinter as tk
import logging

gui_stderr = logging.getLogger(GUI_STDERR)
gui_stdout = logging.getLogger(GUI_STDOUT)

class singleton(type):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance

class AsyncInterface:

    loop = asyncio.get_event_loop()
    tasks = list()

    def __init__(self, delegate):
        self.delegate = delegate

    def forward(self, request, *args, **kwargs):
        if hasattr(self.delegate, request):
            function = object.__getattribute__(self.delegate, request)
            assert callable(function) and not asyncio.iscoroutine(function)
            function(*args, **kwargs)
        else:
            raise NotImplementedError
    
    async def async_forward(self, request, *args, **kwargs):
        if hasattr(self.delegate, request):
            function = object.__getattribute__(self.delegate, request)
            assert callable(function) and asyncio.iscoroutine(function)
            await function(*args, **kwargs)
        else:
            raise NotImplementedError
    
    def add_task(self, task):
        self.tasks.append(self.loop.create_task(task))
    


class AsyncTk(AsyncInterface, tk.Tk, metaclass=singleton):

    update_tasks = list()
    instance = None
    
    def __init__(self, delegate=None, title=None, refreshrate=None):
        super().__init__(delegate)
        tk.Tk.__init__(self)

        if isinstance(title, str):
            self.wm_title(title)
        if refreshrate is None:
            refreshrate = 60
        self.interval = 1 / refreshrate
        self.bind("<Escape>", self.destroy)
    
    def update(self):
        for update_task in self.update_tasks:
            try:
                update_task()
            except:
                self.update_tasks.remove(update_task)
                gui_stderr.exception("")
        super().update()

    def add_task(self, task):
        self.tasks.append(self.loop.create_task(task))

    @log_info("System Initiated", time=True)
    def mainloop(self):
        async def _mainloop():
            while True:
                self.update()
                await asyncio.sleep(self.interval)
    
        self.tasks.append(self.loop.create_task(_mainloop()))
        self.loop.run_forever()
    
    def destroy(self, *args):
        for task in self.tasks:
            task.cancel()
        super().destroy()
        self.loop.stop()
    
    def __call__(self):
        self.mainloop()
      
def update(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        function = partial(func, *args, **kwargs)
        object.__setattr__(function, "__name__", name)
        AsyncTk().update_tasks.append(function)
    return wrapper




    
    


