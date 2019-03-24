import functools
import tkinter as tk
import websockets
import asyncio
import subprocess
import multiprocessing
import json
import logging

def kill_server(port=None):
    """kill program connected to port"""
    if port is None:
        port = 8080
    
    port = int(port)
    try:
        sub = subprocess.check_output(f"lsof -i:{port}", shell=True, stderr=subprocess.STDOUT)
        output = sub.decode().split("\n")
        lines = list()
        ids = set()
        for line in output:
            if "python" in line:
                lines.append(line)
        
        for line in lines:
            ids.add(line.split()[1])
    except:
        ids = None
    finally:
        if ids is not None and ids != {}:
            [subprocess.call(f"kill {ppid}", shell=True) for ppid in ids]
            print("done")  
        else:
            print(f"{port} is clear.")

logger = logging.getLogger("websockets")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class server_test:

    messages = list()
    available_ports = {"7000","8000", "9000"}
    clients = dict()
    

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.run()
    
    async def handler(self, ws, *args, **kwargs):
        async for message in ws:
            message = json.loads(message)
            if message["request"] == "new message":
                self.messages.append(message["data"])
                print(message)
            
            elif message["request"] == "connect":
                client_id = message["id"]
                self.clients[client_id] = await self.on_connect(ws, *args)
            
            elif message["request"] == "disconnect":
                await self.on_disconnect(ws, client_id=message["id"])

    async def on_connect(self, ws, *args):
        """create a websocket server for continuous updates"""
        try:
            port = self.available_ports.pop()
            logger.info(f"connecting to {port}")
            
        except:
            logging.error("no more ports available")
            await ws.send(json.dumps({"port":False}))
            return

        try:
            result = await websockets.serve(self.update_handler, "localhost", port)
            logger.info(f"created handler {result}")
            await ws.send(port)
            return result, port

        except:
            logger.error(f"failed to create handler")
            await ws.send(json.dumps({"port": False}))
    
    async def on_disconnect(self, ws, *args, **kwargs):
        client_id = kwargs["client_id"]
        try:
            server, port = self.clients[client_id]
        except KeyError:
            logging.error(f"client '{client_id}' is not connected")
        
        try:
            server.close()
            self.available_ports.add(port)
            logging.info(f"client '{client_id}' disconnected")
        except:
            logging.error("failed to close connection handler")


    async def update_handler(self, ws, *args, **kwargs):
        async for message in ws:
            message = json.loads(message)
            if message["request"] == "update":
                await ws.send("\n".join(self.messages))

        
    def run(self):
        self.loop.run_until_complete(websockets.serve(self.handler, "localhost", "8080"))
        self.loop.run_forever()





class client_test(tk.Tk):



    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
        self.loop = asyncio.get_event_loop()
        self.string = tk.StringVar(self)
        entry = tk.Entry(self, textvariable=self.string)
        self.button = tk.Button(self, text="Send", command=self.button_command)
        self.connect_button = tk.Button(self, text="connect", command=self.connect_command)
        self.disconnect_button = tk.Button(self, text="disconnect", command=self.disconnect_command)
        
        

        entry.grid(row=0, column=0, sticky="nswe")
        self.button.grid(row=0, column=1, sticky="nswe")
        self.connect_button.grid(row=1, column=0, sticky="nswe")
        self.disconnect_button.grid(row=1, column=1, sticky="nswe")
        self.bind("<Escape>", self.destroy)
        self.connection = False
        self.port = None
        self.mainloop()

    def button_command(self):
        async def command():
            async with websockets.connect("ws://localhost:8080") as ws:
                await ws.send(json.dumps({"request": "new message", "data": self.string.get()}))
        self.loop.create_task(command())
    
    def connect_command(self):
        async def command():
            async with websockets.connect("ws://localhost:8080") as ws:
                await ws.send(json.dumps({"request": "connect", "id": self.client_id}))
                self.port = await ws.recv()
            
            
            async with websockets.connect(f"ws://localhost:{self.port}") as ws:
                self.connection = True
                while self.connection:              
                    await ws.send(json.dumps({"request":"update"}))
                    print(f"{self.client_id}: " + await ws.recv())
                    await asyncio.sleep(1)
                else:
                    await ws.send(json.dumps({"request":""}))
        self.loop.create_task(command())
    
    def disconnect_command(self):
        async def command():
            self.connection = False
            await asyncio.sleep(1)
            async with websockets.connect("ws://localhost:8080") as ws:
                await ws.send(json.dumps({"request": "disconnect", "id": self.client_id}))
        
        self.loop.create_task(command())


    def mainloop(self):
        async def inner():
            while True:
                self.update()
                await asyncio.sleep(1/60)
        self.loop.create_task(inner())        
     
        self.loop.run_forever()

    def destroy(self, *args):
        self.loop.stop()
        super().destroy()
        kill_server()
        


switch = {
    "client":functools.partial(client_test, "client1"),
    "server":functools.partial(server_test),
    "client2": functools.partial(client_test, "client2")
}

def process(arg):
    switch.get(arg)()

def main():
    pool = multiprocessing.Pool(3)
    pool.map(process, ["client", "server", "client2"])
