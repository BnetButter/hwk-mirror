import websockets
import lib
import json
import asyncio
import csv

LOCAL_PATH = "./sales.csv"

async def get_data():
    async with websockets.connect(lib.address) as ws:
        await ws.send(json.dumps({"client_id": "Extern", "request": "extract", "data": None}))
        return json.loads(await ws.recv())["result"]

def write_local(task):
    result = task.result()
    with open(LOCAL_PATH, "w") as fp:
        writer = csv.writer(fp)
        for line in result:
            writer.writerow(line)
    print("Saved to local storage")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(get_data())
    task.add_done_callback(write_local)
    loop.run_until_complete(task)


