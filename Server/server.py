from lib import ServerInterface
from datetime import datetime
import json
import operator
import lib
import asyncio
import subprocess

class Server(ServerInterface):
    
    def __init__(self):
        super().__init__()
        self.salesinfo = lib.SalesInfo(lib.SALESLOG)

    async def new_order(self, ws, data):
        self.order_queue[self.ticket_no] = data
        await ws.send(json.dumps({"result":self.ticket_no}))
        self.ticket_no += 1
    
    async def cancel_order(self, ws, data):
        ticket = self.order_queue.pop(data)
        await ws.send(json.dumps({"result":ticket}))
        
    async def modify_order(self, ws, data):
        ticket_no, modified = data
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
        parameters = operator.itemgetter(5)
        parameters(ticket[:6])["status"] = value
        parameters(ticket[6])["status"] = value
        parameters(ticket[7])["status"] = value
        await ws.send(json.dumps({"result":(True, None)}))
        if self.order_complete(ordered_items):
            self.salesinfo.write(self.order_queue[ticket_no])
            self.order_queue.pop(ticket_no)
    
    async def set_order_status(self, ws, data):    
        ticket_no, value = data
        if ticket_no not in self.order_queue:
            await ws.send(json.dumps({"result":(False, f"ticket no. {ticket_no} does not exist")}))
        else:
            parameters = operator.itemgetter(5)
            for ticket in self.order_queue[ticket_no]["items"]:
                parameters(ticket[:6])["status"] = value
                parameters(ticket[6])["status"] = value
                parameters(ticket[7])["status"] = value
            await ws.send(json.dumps({"result":(True, None)}))
        
        if self.order_complete(self.order_queue[ticket_no]["items"]):
            self.salesinfo.write(self.order_queue[ticket_no])
            self.order_queue.pop(ticket_no)

    async def set_item_status(self, ws, data):
        ticket_no, nth_ticket, item_idx, value = data
        if ticket_no not in self.order_queue:
            return await ws.send(json.dumps({"result":(False, f"ticket no. {ticket_no} does not exist")}))
        
        ticket = self.order_queue[ticket_no]["items"][nth_ticket]
        item = {0:ticket, 1:ticket[6], 2:ticket[7]}.get(item_idx)
        if not item[1]:
            return await ws.send(json.dumps({"result": (False, f"Cannot set status of empty ticket")}))
        item[5]["status"] = value
        return await ws.send(json.dumps({"result":(True, None)}))

    async def remove_completed(self, ws, data):    
        for ticket_no in self.order_queue:
            if self.order_complete(self.order_queue[ticket_no]["items"]):
                self.order_queue.pop(ticket_no)
        return await ws.send(json.dumps({"result": (True, "")}))
    
    @staticmethod
    def order_complete(items):    
        valid_items = (item 
                for ticket in items
                    for item in (ticket, ticket[6], ticket[7])
                        if item[1])
        return all(item[5].get("status") == lib.TICKET_COMPLETE
                for item in valid_items)

    async def get_time(self, ws, data):
        await ws.send(json.dumps({"result":(True, int(datetime.now()))}))
    
    async def global_shutdown(self, ws, data):
        self.shutdown_now = data
        await ws.send(json.dumps({"result":(True, None)}))
        self.loop.create_task(self.shutdown())
        
    async def edit_menu(self, ws, data):
        print(data)
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
                break