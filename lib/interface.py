from abc import ABCMeta
from abc import abstractmethod
from collections import OrderedDict
import time
import websockets
import json
import logging
import asyncio
import functools
import subprocess
import sys
import decimal
import os


from .data import address, device_ip, port, router_ip
from .data import APPDATA
from .data import ASCIITIME, LEVEL_NAME, MESSAGE
from .data import GUI_STDOUT, GUI_STDERR
from .globalstate import GlobalState

logger = logging.getLogger("websockets")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(f"{ASCIITIME} - {LEVEL_NAME} - {MESSAGE}"))
logger.addHandler(handler)


class Pointer:
    __slots__ = ["_value"]

    def __init__(self, value=None):
        self._value = value
    
    def __repr__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value



class ServerInterface(GlobalState, metaclass=ABCMeta):
    loop = asyncio.get_event_loop()
    available_ports = {"7000", "8000", "9000"}
    clients = dict()

    def __init__(self):
        super().__init__()
        self.order_queue = OrderedDict()
        self.ticket_no = 1
        self.shutdown_now = False
        self.connected_clients = dict()
        self.coroutine = self.coroutine_switch()

    async def on_connect(self, ws, client_id) -> tuple:
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
                    self.update_handler, device_ip, port)
            logger.info(f"Server created for '{client_id}' on port {port}")
            await ws.send(json.dumps({"result": port}))
            return server, port

        except:
            logger.critical(f"Failed to create server for client '{client_id}'")
            await ws.send(json.dumps({"port":False}))
    
    async def on_disconnect(self, ws, client_id):
        """closes the server object"""
        try:
            server, port = self.clients[client_id]
        except KeyError:
            logger.warning(f"'{client_id}' is not connected")
            await ws.send(json.dumps({"result":False}))
            return

        try:
            server.close()
            self.available_ports.add(port)
            logger.info(f"{client_id}: disconnected")
            await ws.send(json.dumps({"result":True}))
        except:
            logger.warning(f"{client_id}: Failed to close connection")
            await ws.send(json.dumps({"result": False}))

    async def server_handler(self, ws, *args, **kwargs):
        async for message in ws:
            client_id, request, data = self.client_message(message)

            if request == "echo":
                await ws.send(json.dumps({"result":message}))
    
            elif request == "connect":
                self.clients[client_id] = await self.on_connect(ws, client_id)
    
            elif request == "disconnect":
                await self.on_disconnect(ws, client_id)
        
            else:
                await self.coroutine(ws, client_id, request, data)
    
    async def update_handler(self, ws, *args, **kwargs):
        async for message in ws:
            if message == "update":
                await ws.send(self.dumps())
            elif message == "disconnect":
                return await ws.send(self.dumps())
    
    def mainloop(self):
        self.loop.run_until_complete(websockets.serve(self.server_handler, device_ip, port))
        self.loop.run_forever()

    def coroutine_switch(self):

        pos = {
            "new_order":self.new_order,
            "global_shutdown":self.global_shutdown,
            "get_time": self.get_time,
            "get_menu": self.get_menu,
            "modify_order": self.modify_order,
            "cancel_order":self.cancel_order,
        }
        display = {
            "order_complete":self.order_complete
        }

        extern = {
        }
        switch = {
            "POS":pos,
            "Display":display,
            "Extern": extern
        }

        async def task(ws, client_id, request, data):
            task = switch.get(client_id)
            if task is None:
                logger.error(f"Unknown client: {client_id}")
                raise ValueError
        
            task = task.get(request)
            if task is None:
                logger.error(f"Unknown request: {request}")
                raise ValueError

            logger.info(f"Received '{request}' from {client_id}") 
            
            try:
                return await task(ws, data)
            except:
                logger.critical(f"Failed to process '{request}' from {client_id}")

        return task
    
    @abstractmethod
    async def new_order(self, ws, client_message):
        client_message = json.dumps({"result":client_message})
        await ws.send(client_message)
    
    @abstractmethod
    async def global_shutdown(self):
        ...
    
    @abstractmethod
    async def get_time(self):
        ...
    
    @abstractmethod
    async def order_complete(self):
        ...
    
    @abstractmethod
    async def modify_order(self):
        ...
    
    @abstractmethod
    async def cancel_order(self):
        ...
    
    @abstractmethod
    async def get_menu(self):
        ...
    
    
    


class ClientInterface(GlobalState):
    
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
        self.loop = asyncio.get_event_loop()
        self.tasks = list()
        self.shutdown_now = Pointer(False)
        self._connected = None
        
        self.log = logging.getLogger(f"main.{self.client_id}.interface")
        self.log.setLevel(logging.WARNING)

        date = time.strftime("%m-%d-%y", time.localtime())
        handler = logging.FileHandler(filename=os.path.join(APPDATA, "logs", f"{date}-{self.client_id}.log"))
        handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.log.addHandler(handler)
    
    async def server_message(self, request, data):
        async with websockets.connect(address) as ws:
            await ws.send(json.dumps({"client_id":self.client_id, "request":request, "data":data}))
            return json.loads(await ws.recv())["result"]
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, value):
        self._connected = value

    def create_task(self, task):
        task = self.loop.create_task(task)
        self.tasks.append(task)
        return task

    def append(self, coro):
        @functools.wraps(coro)
        def wrapper(*args, **kwargs):
            task = self.loop.create_task(coro(*args, **kwargs))
            self.tasks.append(task)
            return task
        return wrapper
    
    def connect(self):
        @self.append
        async def coroutine():
            async with websockets.connect(address) as ws:
                port = await self.server_message("connect", None)
                if not port:
                    # stderr.error("ERROR: Server host failed to assign update server")
                    raise Exception("Server host failed to assign update server")

            async with websockets.connect(f"ws://{device_ip}:{port}") as ws:
                self.connected = True
                while True:
                    if self.connected:
                        await ws.send("update")
                        self.loads(await ws.recv())
                        await asyncio.sleep(1/30)
                    else:
                        await ws.send("disconnect")
                        self.loads(await ws.recv())
                        break
        
            return await self.server_message("disconnect", None)
        return coroutine()
        
    def disconnect(self, *args):
        self.connected = False


    def close(self):
        for task in self.tasks:
            task.cancel()


    def test_network_connection(self):    
        @self.append
        async def coroutine():  
            while True:
                self.network = subprocess.call(f"ping -c 1 {router_ip}",
                    shell=True, 
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL) == 0
                await asyncio.sleep(5)
        coroutine()
    

class POSInterface(ClientInterface, metaclass=ABCMeta):

    def __init__(self):
        super().__init__("POS")
    
    @abstractmethod
    def new_order(self):...        

    @abstractmethod
    def edit_order(self):...
    
    @abstractmethod
    def cancel_order(self):...
    
    @abstractmethod
    def global_shutdown(self):...
    
    @abstractmethod
    def edit_menu(self):...
    
    @abstractmethod
    def get_connection_status(self):...

    @abstractmethod
    def get_ticket_no(self):...

    @abstractmethod
    def get_time(self):...    
    
    @abstractmethod
    def get_order_status(self):...


    
    
