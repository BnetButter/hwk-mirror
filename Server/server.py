from lib import ServerInterface
from datetime import datetime
from .loggers import SalesLogger
from .loggers import EventLogger
import time
import json
import operator
import lib
import asyncio
import subprocess
import collections
import multiprocessing

class Server(ServerInterface):
        
    def __init__(self):
        super().__init__()
        self.api_queue = multiprocessing.Queue()
        self.saleslogger = SalesLogger()
        self.canceled_tickets = asyncio.Queue()
        self.completed_tickets = asyncio.Queue()
        self.loop.create_task(self.remove_cancelled())
        self.loop.create_task(self.remove_completed())
        self.loop.create_task(self.set_completed())
        self.loop.create_task(self.saleslogger.logger())

    def request_response(self):
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
            "get_time": self.get_time,
        }

        extern = {
            "extract": self.extract,
            "ping": self.ping
        }
        
        return {
            "POS":pos,
            "Display":display,
            "Extern": extern
        }

    async def ping(self, ws, data):
        await ws.send(json.dumps({"result":True}))

    async def new_order(self, ws, data):
        data["items"] = [lib.Ticket.convert_to(*ticket) for ticket in data["items"]]
        self.order_queue[self.ticket_no] = data
        await ws.send(json.dumps({"result":self.ticket_no}))
        self.ticket_no += 1
    
    async def set_ticket_printed(self, ws, data):
        ticket = self.order_queue[int(data)]
        ticket["print"] = False
        await ws.send(json.dumps({"result": (True, None)}))

    async def cancel_order(self, ws, data):
        # set order status as complete
        ticket = self.order_queue[data]
        await self.canceled_tickets.put(data)
        self.order_queue[data]["print"] = lib.PRINT_NUL
        await ws.send(json.dumps({"result":ticket}))

    async def set_completed(self):
        while True:
            for ticket in self.order_queue:
                if self.order_complete(self.order_queue[ticket]["items"]):
                    await self.completed_tickets.put(ticket)
            await self.completed_tickets.join()
            await asyncio.sleep(1/30)
        
    async def remove_completed(self):
        while True:
            number = await self.completed_tickets.get()
            while self.order_queue[number]["print"]:
                await asyncio.sleep(1/60)
            self.logger.info("completed ticket no. {:03d}".format(number))
            result = self.order_queue.pop(number)
            self.completed_tickets.task_done()
            await self.saleslogger.write(result)
            
    async def remove_cancelled(self):
        while True:
            number = await self.canceled_tickets.get()
            while self.order_queue[number]["print"]:
                await asyncio.sleep(1/60)
            self.order_queue.pop(number)
            self.canceled_tickets.task_done()

    async def modify_order(self, ws, data):
        ticket_no, modified = data
        modified["items"] = [lib.Ticket.convert_to(*item) for item in modified["items"]]
        if ticket_no not in self.order_queue:
            await ws.send(json.dumps({"result":(False, f"ticket no. {ticket_no} does not exist")}))
        else:
            self.order_queue[ticket_no] = modified
            await ws.send(json.dumps({"result":(True, None)}))

    async def set_ticket_status(self, ws, data):
        ticket_no, nth_ticket, value = data
        if ticket_no not in self.order_queue:
            return await ws.send(json.dumps({"result":(False, f"ticket no. {ticket_no} does not exist")}))
        
        ordered_items = self.order_queue[ticket_no]["items"]
        ticket = ordered_items[nth_ticket]
        ticket.parameters["status"] = value
        ticket.addon1.parameters["status"] = value
        ticket.addon2.parameters["status"] = value
        await ws.send(json.dumps({"result":(True, None)}))
    
    async def set_order_status(self, ws, data):    
        ticket_no, value = data
        if ticket_no not in self.order_queue:
            await ws.send(json.dumps({"result":(False, f"ticket no. {ticket_no} does not exist")}))
        else:
            for ticket in self.order_queue[ticket_no]["items"]:
                ticket.parameters["status"] = value
                ticket.addon1.parameters["status"] = value
                ticket.addon2.parameters["status"] = value
            await ws.send(json.dumps({"result":(True, None)}))

    async def set_item_status(self, ws, data):
        ticket_no, nth_ticket, item_idx, value = data
        if ticket_no not in self.order_queue:
            return await ws.send(json.dumps({"result":(False, f"ticket no. {ticket_no} does not exist")}))
        
        ticket = self.order_queue[ticket_no]["items"][nth_ticket]
        item = {0:ticket, 1:ticket.addon1, 2:ticket.addon2}.get(item_idx)
        if not item.name:
            return await ws.send(json.dumps({"result": (False, f"Cannot set status of empty ticket")}))
        item.parameters["status"] = value
        return await ws.send(json.dumps({"result":(True, None)}))
        
    @staticmethod
    def order_complete(items):
        valid_items = (item 
                for ticket in items
                    for item in (ticket, ticket.addon1, ticket.addon2)
                        if item.name)

        return all(item.parameters.get("status") == lib.TICKET_COMPLETE
                for item in valid_items)

    async def get_time(self, ws, data):
        await ws.send(json.dumps({"result":int(time.time())}))
    
    async def global_shutdown(self, ws, data):
        self.shutdown_now = data
        await ws.send(json.dumps({"result":(True, None)}))
        self.loop.create_task(self.shutdown())
        
    async def edit_menu(self, ws, data):
        with open(lib.MENUPATH, "w") as fp:
            json.dump(data, fp, indent=4)
            return await ws.send(json.dumps({"result":(True, None)}))
        return await ws.send(json.dumps({"result": (False, "Failed to write menu")}))

    async def get_menu(self, ws, data):
        with open(lib.MENUPATH, "r") as fp:
            await ws.send(json.dumps({"result": (True, json.load(fp))}))
        return await ws.send(json.dumps({"result": (False, f"Failed to read menu at {lib.MENUPATH}")}))

    async def shutdown(self):
        while True:
            await asyncio.sleep(1/30)
            # wait for clients to disconnect
            if not self.clients:
                self.loop.stop()
                await self.saleslogger.join()
                break
    
    async def extract(self, ws, data):
        await ws.send(json.dumps({"result": self.saleslogger.data()}))