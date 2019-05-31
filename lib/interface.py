from abc import ABCMeta
from abc import abstractmethod
from collections import OrderedDict
from collections import deque
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
import io

from .data import address, device_ip, port, router_ip
from .data import APPDATA
from .data import ASCIITIME, LEVEL_NAME, MESSAGE
from .data import GUI_STDOUT, GUI_STDERR
from .tkinterface import AsyncTk

logger = logging.getLogger("websockets")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(f"{ASCIITIME} - {LEVEL_NAME} - {MESSAGE}"))
logger.addHandler(handler)



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


class ServerInterface(GlobalState, metaclass=ABCMeta):
    loop = asyncio.get_event_loop()
    available_ports = {"7000", "8000", "9000"}
    clients = dict()

    def __init__(self):
        super().__init__()
        self.order_queue = OrderedDict()
        self.ticket_no = 1
        self.shutdown_now = False
        self.coroutine = self.coroutine_switch()
        self.logger = logger

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
            server, port = self.clients.pop(client_id)
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
                self.connected_clients = [client_id for client_id in self.clients]
    
            elif request == "disconnect":
                await self.on_disconnect(ws, client_id)
                self.connected_clients = [client_id for client_id in self.clients]
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
            "edit_menu": self.edit_menu,
            "modify_order": self.modify_order,
            "cancel_order":self.cancel_order,
            "get_menu": self.get_menu,
        }
        display = {
            "order_complete":self.order_complete,
            "set_ticket_status": self.set_ticket_status,
            "set_order_status": self.set_order_status,
            "set_item_status": self.set_item_status,
            "set_ticket_printed": self.set_ticket_printed,
        }

        extern = {
            "extract": self.extract
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
    async def new_order(self):
        ...
    
    @abstractmethod
    async def set_item_status(self):
        ...
    
    @abstractmethod
    async def set_order_status(self):
        ...
    
    @abstractmethod
    async def set_ticket_status(self):
        ...
    
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
    async def edit_menu(self):
        ...

    @abstractmethod
    async def get_menu(self):
        ...

    @abstractmethod
    async def remove_completed(self):
        ...
    
    @abstractmethod
    async def extract(self):
        ...

    @abstractmethod
    async def set_ticket_printed(self):
        ...

class ClientInterface(GlobalState):

    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
        self.loop = asyncio.get_event_loop()
        self.tasks = list()
        self.shutdown_now = False
        self.network = None
        self.connected = None
        
        self.log = logging.getLogger(f"main.{self.client_id}.interface")
        self.log.setLevel(logging.WARNING)

    
    async def server_message(self, request, data):
        async with websockets.connect(address) as ws:
            await ws.send(json.dumps({"client_id":self.client_id, "request":request, "data":data}))
            return json.loads(await ws.recv())["result"]

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

        # if server is not online when client starts, wait for server
        async def get_port():
            while True:
                try:
                    return await self.server_message("connect", None)
                except:
                    await asyncio.sleep(1)

        @self.append
        async def coroutine():    
            while True:
                try:
                    task = self.loop.create_task(get_port())
                    result = await asyncio.wait({task})
                    assert task in result[0]
                    self.connected = True
                    ws = await websockets.connect(f"ws://{device_ip}:{task.result()}")
                    while True:
                        if self.connected:
                            await ws.send("update")
                            self.loads(await ws.recv())
                            await asyncio.sleep(1/30)
                        else:
                            # tell update handler to stop
                            await ws.send("disconnect")
                            self.loads(await ws.recv())
                            break
                    # tell server handler to do cleanup
                    return await self.server_message("disconnect", None)
                except:
                    self.connected = False
                finally:
                    await asyncio.sleep(1)
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
    
    def get_connection_status(self):
        return self.network, self.connected, self.connected_clients
    
    def shutdown(self, cleanup=lambda: None, shutdown_system=False):
        async def shutdown():
            while True:
                if self.shutdown_now:
                    await asyncio.sleep(self.shutdown_now)
                    cleanup()
                    if shutdown_system:
                        subprocess.call("shutdown -h now")
                else:
                    await asyncio.sleep(1/30)
        self.loop.create_task(shutdown())

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
    def get_ticket_no(self):...

    @abstractmethod
    def get_time(self):...    
    
    @abstractmethod
    def get_order_status(self):...


class DisplayInterface(ClientInterface):

    def __init__(self):
        super().__init__("Display")
    
    @abstractmethod
    def set_ticket_status(self):
        ...
    
    @abstractmethod
    def set_order_status(self):
        ...