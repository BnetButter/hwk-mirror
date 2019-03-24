from .default_protocol import POSProtocolBase
import functools
from lib import GUI_STDERR, GUI_STDOUT
from lib import address, device_ip, router_ip
from lib import GlobalState
from POS import Order, NewOrder
import websockets
import asyncio
import json
import logging
import functools
import subprocess

logger = logging.getLogger("websockets")
logger.addHandler(logging.StreamHandler())
stderr = logging.getLogger(GUI_STDERR)
stdout = logging.getLogger(GUI_STDOUT)

def server_request(client_id, request, data):
    assert isinstance(client_id, str) and isinstance(request, str)
    try:
        message = json.dumps({"client_id":client_id, 
                "request":request,
                "data": data})
    except:
        stderr.error(f"Failed to decode '{request.replace('_', ' ')}' request: {data}")        
        raise ValueError(f"Failed to decode '{request.replace('_', ' ')}' request: {data}")
    return message

class POSProtocol(GlobalState, POSProtocolBase):
    
  
    loop = asyncio.get_event_loop()
    tasks = list()
    client_id = "POS"

    def __init__(self):
        super().__init__()
        self.network = False
        self.connected = False
        
        self.test_network_connection()
        self.connect()
        

        

    def get_ticket_no(self, result):
        if self.ticket_no is not None:
            ticket_no = "{:03d}".format(self.ticket_no)
            result.set(ticket_no)
        
    def append(self, coroutine):
        self.tasks.append(self.loop.create_task(coroutine()))

    def new_order(self, payment_type, cash_given, change_due, *args, **kwargs):
        order_dct = dict()
        for i, ticket in enumerate(Order()):
            order_dct[i] = list(ticket)

        order_dct["total"] = Order().total
        order_dct["subtotal"] = Order().subtotal
        order_dct["tax"] = Order().tax
        order_dct["payment_type"] = payment_type
        order_dct["cash_given"] = cash_given
        order_dct["change_due"] = change_due

        async def coroutine():
            async with websockets.connect(address) as ws:
                await ws.send(server_request(self.client_id, "new_order", order_dct))
                result = json.loads(await ws.recv())["result"]          
                stdout.info(f"Server received ticket no {'{:03d}'.format(result)}")
                NewOrder()

        self.append(coroutine)
    
    def connect(self):
        async def coroutine():
            async with websockets.connect(address) as ws:
                await ws.send(server_request("POS", "connect", None))
                port = json.loads(await ws.recv())["result"]
                if not port:
                    stderr.error("ERROR: Server host failed to assign update server")
                    return Exception
            

            async with websockets.connect(f"ws://{device_ip}:{port}") as ws:
                self.connected = True
                while self.connected:
                    await ws.send("update")
                    self.loads(await ws.recv())
                    await asyncio.sleep(1/30)

        self.append(coroutine)
    
    def disconnect(self):
        async def coroutine():
            self.connection = False
            await asyncio.sleep(1/30)
            async with websockets.connect(address) as ws:
                await ws.send("disconnect")
        self.append(coroutine)
    
    def get_connection_status(self, network_indicator, server_indicator, display_indicator):
        network_indicator.set(self.network)
        server_indicator.set(self.connected)
        if self.connected_clients is None:
            display_indicator.set(False)
        else:
            display_indicator.set("Display" in self.connected_clients)

    def test_network_connection(self):
        def test_network():
            result = subprocess.call(f"ping -c 1 {router_ip}",
                    shell=True, 
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL)
            
            if result == 0:
                self.network = True
            else:
                self.network = False
                stdout.critical(f"CRITICAL ERROR: Cannot connect to router at {router_ip}")

           

        async def coroutine():  
            while True:
                await self.loop.run_in_executor(None, test_network)
                await asyncio.sleep(5)
        
        self.append(coroutine)

    def close(self):
        self.disconnect()
        for task in self.tasks:
            task.cancel()


    

            