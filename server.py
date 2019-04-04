from lib import ServerInterface
import json

class Server(ServerInterface):
    
    async def new_order(self, ws, data):
        self.order_queue[self.ticket_no] = data
        await super().new_order(ws, self.ticket_no)
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

    def get_time(self): ...
    
    def global_shutdown(self): ...

    def order_complete(self): ...
    
    def get_menu(self): ...
    

def main():
    Server().mainloop()