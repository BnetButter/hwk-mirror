from functools import wraps
from .tkwidgets import AsyncWindow
import asyncio
import json

class EventManagerType(type):
    events = list()
    delegates = dict()
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exec()

    def __call__(self, **kwargs):
        assert all(callable(value) for value in kwargs.values())
        self.delegates.update(kwargs)

    @AsyncWindow.update_function
    def exec(self):
        for event in self.events:
            request = event["request"]
            if request in self.delegates:
                self.delegates[request](*event["args"], 
                        **event["kwargs"])
                self.events.remove(event)
    
    def delegate(self, name):
        if name in self.delegates:
            raise KeyError(f"Request tag '{name}' already exists")
        def _delegate(func):
            assert callable(func)
            self.delegates.update({name: func})
        return _delegate

    def forward(self, request:str, *args, **kwargs):
        self.events.append(
            {"request":request, 
             "args": args,
             "kwargs": kwargs})

Event = EventManagerType("Event", (object,), {})

    