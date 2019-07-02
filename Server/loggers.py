import lib
import time
import socket
import asyncio
import GoogleDrive
import os
import json


class SalesLogger(lib.SalesInfo):

    def __init__(self):
        date = time.strftime("%m-%d-%y", time.localtime())
        super().__init__(lib.SALESLOG + ".csv")
        self.api = GoogleDrive.SheetsAPI(lib.TOKEN, lib.CREDENTIALS)
        self.sheet_title = date
        self.new_sales_sheet()
        self.queue = asyncio.Queue()
    
    def test_connection(self):
        try:
            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except:
            return False

    def new_sales_sheet(self):
        async def _api_call():
            try:
                await self.api.add_sheet(lib.SALESLOG_SPREADSHEET_ID, self.sheet_title)
                await self.api.append(lib.SALESLOG_SPREADSHEET_ID, f"'{self.sheet_title}'!A1:F2", 
                    [self.headers])
            except:
                # add logging
                return 0
        asyncio.get_event_loop().run_until_complete(_api_call())

    async def write(self, data):
        super().write(data)
        await self.queue.put(data)

    # unblock api.append
    async def logger(self):
        while True:
            data = await self.queue.get()
            content = list(self.to_csv(data))
            content[5] = str(content[5])
            content = [content]
            try:
                await self.api.append(lib.SALESLOG_SPREADSHEET_ID,
                        f"'{self.sheet_title}'!A1:F", content)
                self.queue.task_done()
            except:
                await asyncio.sleep(1/60)
    
    async def join(self):
        await self.queue.join()


class EventLogger:
    
    def write(self, content):
        ...
    

