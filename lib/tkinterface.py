from functools import wraps
from functools import partial
from operator import itemgetter
from .data import GUI_STDERR
from .data import GUI_STDOUT
from .data import output_message
from .stream import stdout, stderr
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
            attribute = object.__getattribute__(self.delegate, request)
            if not callable(attribute):
                return attribute
            assert not asyncio.iscoroutine(attribute)
            return attribute(*args, **kwargs)
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
        self.running = False
    
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

    def mainloop(self):

        async def _mainloop():
            self.running = True
            while self.running:
                self.update()
                await asyncio.sleep(self.interval)
            else:
                self.forward("disconnect")
                await asyncio.sleep(self.interval * 2)
                for task in self.tasks:
                    task.cancel()
                self.loop.stop()
        
        logger = logging.getLogger(f"main.{self.delegate.client_id}.gui")
        stdout_stream = logging.StreamHandler(stream=stdout)
        stdout_stream.addFilter(logging.Filter(f"{logger.name}.stdout"))
        stderr_stream = logging.StreamHandler(stream=stderr)
        stderr_stream.addFilter(logging.Filter(f"{logger.name}.stderr"))
        
        logger.addHandler(stdout_stream)
        logger.addHandler(stderr_stream)
        self.loop.create_task(_mainloop())

        logging.getLogger(f"{logger.name}.stdout").info("System Initiated")
        self.loop.run_forever()
    
    def destroy(self, *args):
        super().destroy()
        self.running = False
        
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




    
    


