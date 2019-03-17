from .tkwidgets import update, async_update
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
        AsyncWindow.append(self.exec)

    def __call__(self, **kwargs):
        assert all(callable(value) for value in kwargs.values())
        self.delegates.update(kwargs)

    @update
    def exec(self):
        for event in self.events:
            request = event["request"]
            if request in self.delegates:
                self.delegates[request](*event["args"], 
                        **event["kwargs"])
                self.events.remove(event)

    def forward(self, message):
        assert isinstance(message, dict)
        self.events.append(message)


Event = EventManagerType("Event", (object,), {})

    