from .stream import stdin
import asyncio

class EventManager:
    """Callback interface for gui events"""
    delegates = dict()

    @classmethod
    def register(cls, name, **kwargs):
        cls.delegates[name] = kwargs
    
    