from abc import ABCMeta
from lib import CONFIGDATA
from lib import abstract_server
from lib import ServerInterface
import websockets
import csv
import json
import asyncio


class Server(abstract_server, metaclass=ServerInterface):
    
    instance = None
    

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        pass
    
    def run(self):
        Server.loop.run_until_complete(
                Server.serve(self.server_handler))
        Server.loop.run_forever()

    async def server_handler(self, ws, *args, **kwargs):
        pass
        