import json

class GlobalState:
    """Base class containing global system variables"""

    __slots__ = ["ticket_no",
                "order_queue", 
                "connected_clients",
                "requests",
                "completed"]

    def __init__(self):
        self.ticket_no = None
        self.order_queue = None
        self.requests = None        
        self.connected_clients = None
        self.completed = None

    def loads(self, string):
        result = json.loads(string)
        self.ticket_no = result["ticket_no"]
        self.order_queue = result["order_queue"]
        self.requests = result["requests"]
        self.connected_clients = result["connected_clients"]
        self.completed = result["completed"]
    
    def dumps(self):
        dct = {
            "ticket_no": self.ticket_no,
            "order_queue": self.order_queue,
            "requests": self.requests,
            "connected_clients": self.connected_clients,
            "completed": self.completed}
        return json.dumps(dct)
    
    
