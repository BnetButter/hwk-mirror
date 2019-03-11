import tkinter as tk
import asyncio

class AsyncWindow(tk.Tk):
    
    def __init__(self, refresh_rate=60, **kwargs):
        super().__init__(**kwargs)
        self.loop = asyncio.get_event_loop()
        self.tasks = list()
        self.interval = 1 / refresh_rate
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", self.close)

    def add_task(self, coro, *args):
        self.tasks.append(
            self.loop.create_task(coro(*args)))
    
    async def _update(self):
        while True:
            self.update()
            await asyncio.sleep(self.interval)
    
    def close(self, *args):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()
    
    def mainloop(self):
        self.add_task(self._update)
        self.loop.run_forever()