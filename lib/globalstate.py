from .data import address
from .data import DEBUG
import json
import websockets
import asyncio

class GlobalState:
    """Base class containing global system variables"""
    loop = asyncio.get_event_loop()
    tasks = list()

    __slots__ = ["ticket_no",
                "order_queue", 
                "connected_clients",
                "requests",
                "shutdown_now",
                "client_id"]
    
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.ticket_no = None
        self.order_queue = None
        self.requests = None        
        self.connected_clients = None
        self.shutdown_now = None

    def loads(self, string):
        result = json.loads(string)
        self.ticket_no = result["ticket_no"]
        self.order_queue = result["order_queue"]
        self.requests = result["requests"]
        self.connected_clients = result["connected_clients"]
        self.shutdown_now = result["shutdown_now"]

    def dumps(self):
        dct = {
            "ticket_no": self.ticket_no,
            "order_queue": self.order_queue,
            "requests": self.requests,
            "connected_clients": self.connected_clients,
            "shutdown_now": self.shutdown_now,
            }
        return json.dumps(dct)

    @staticmethod
    def client_message(message):
        message = json.loads(message)
        return message["client_id"], message["request"], message["data"]
