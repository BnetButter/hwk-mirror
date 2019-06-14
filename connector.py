import asyncio
import websockets
import json
import pathlib
import os
import functools

class Connection:
    """Connection().result -> '192.168.x.xxx'"""

    def __init__(self, router_ip, port, start=2, stop=255, skip=1):
        self.loop = asyncio.get_event_loop()
        self.result_queue = asyncio.Queue()
        self._result = None
        self.address = ".".join(router_ip.split(".")[:-1])
        
        self.tasks = list()

        self._args = start, stop, skip
        self.port = port
        

    async def get_result(self):
        await self._get_result()
        return self._result

    @property
    def result(self):
        try:
            task = self.loop.create_task(self._get_result())
            self.loop.run_until_complete(task)
            return self._result
        except:
            return False
    
    async def _get_result(self):
        for i in range(*self._args):
            address = self.address + f".{i}"
            task = self.loop.create_task(self._worker(address))
            self.tasks.append(task)
        self._result = await self.result_queue.get()
        self.result_queue.task_done()
        return True
    
    def _done_cb(self, task):
        print("done")
        for task in self.tasks:
            task.stop()

    async def _worker(self, address):
        ip = f"ws://{address}:{self.port}"
        while True:
            try:
                async with websockets.connect(ip, ping_timeout=0.5) as ws:
                    await ws.send(json.dumps(
                        {"client_id":"Extern", "request":"ping", "data":None}))
                    result = json.loads(await ws.recv())["result"]
                    assert result
                    await self.result_queue.put(address)
                    return address, True
            except:
                await asyncio.sleep(1/30)


if __name__ == "__main__":
    confpath = os.path.join(str(pathlib.Path.home()),".hwk/config.json")
    with open(confpath, "r") as fp:
        config = json.load(fp)

    router_ip, port = config["router"], config["port"]
    config["ip"] = Connection(router_ip, port).result
    with open(confpath, "w") as fp:
       json.dump(config, fp, indent=4)