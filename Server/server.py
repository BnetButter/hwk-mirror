from lib import CONFIGDATA
from lib import device_ip, port
from lib import SYS_STDERR
from lib import LOGPATH
from lib import NAME, FUNC_NAME, MESSAGE, ASCIITIME, LEVEL_NAME
from lib import GlobalState
from collections import OrderedDict
import websockets
import csv
import json
import asyncio
import logging
import sys

logger = logging.getLogger("websockets")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(f"{ASCIITIME} - {LEVEL_NAME} - {MESSAGE}"))
logger.addHandler(handler)
    

class ConnectionMixin:

    available_ports = {"7000", "8000", "9000"}
    clients = dict()

    async def on_connect(self, ws, client_id, update_handler, *args, **kwargs) -> tuple:
        """create a websocket server object connected to port"""
        try:
            port = self.available_ports.pop()
            logger.debug(f"Selected port {port}")
        except:
            logger.warning("No more ports available")
            await ws.send(json.dumps({"result": False}))
            return
        
        try:
            server = await websockets.serve(
                    update_handler, device_ip, port)
            logger.info(f"Server created for '{client_id}' on port {port}")
            await ws.send(json.dumps({"result": port}))
            return server, port

        except:
            logging.critical(f"Failed to create server for client '{client_id}'")
            await ws.send(json.dumps({"port":False}))
    
    async def on_disconnect(self, ws, client_id, *args, **kwargs):
        """closes the server object"""
        try:
            server, port = self.clients[client_id]
        except KeyError:
            logging.warning(f"'{client_id}' is not connected")
            return

        try:
            server.close()
            self.available_ports.add(port)
            logging.info(f"{client_id}: disconnected")
        except:
            logging.warning(f"{client_id}: Failed to close connection")
    

class Server(GlobalState, ConnectionMixin):
    
    loop = asyncio.get_event_loop()
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()        
        self.order_queue = OrderedDict()
        self.ticket_no = 1
        self.connected_clients = dict()
        self.completed = list()
        self.coroutine = self.coroutine_switch()
        
        
    async def server_handler(self, ws, *args, **kwargs):
        async for message in ws:
            message = json.loads(message)
            request = message["request"]
            client_id = message["client_id"]
            data = message["data"]

            if request == "connect":
                self.clients[client_id] = await self.on_connect(ws, client_id, self.update_handler)

            elif request == "disconnect":
                await self.on_disconnect(ws, client_id)

            else:
                await self.coroutine(ws, client_id, request, data)
    
    async def update_handler(self, ws, *args, **kwargs):
        async for message in ws:
            if message == "update":
                await ws.send(self.dumps())
            elif message == "disconnect":
                return

    async def new_order(self, ws, data, *args, **kwargs):
        self.order_queue[self.ticket_no] = data
        await ws.send(json.dumps({"result": self.ticket_no}))
        self.ticket_no += 1
        logger.debug(f"{self.order_queue}")
    
    def coroutine_switch(self):
        pos = {
            "new_order": self.new_order
            # "edit_order": self.edit_order 
            # ...
            # ...
        }
        display = {

        }
        extern = {

        }

        switch = {
            "POS": pos,
            "Display":display,
            "Extern": extern, 
        }

        async def coroutine(ws, client_id, request, data):
            task = switch.get(client_id).get(request)
            return await task(ws, data)
        return coroutine
    
    def mainloop(self):
        self.loop.run_until_complete(websockets.serve(self.server_handler, device_ip, port))
        self.loop.run_forever()


