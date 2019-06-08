import smbus
import functools
import asyncio

class AsyncSMBus:

    def __init__(self, addr=None, port=None, delay=None):
        if addr is None:
            addr = 27
        if port is None:
            port = 1
        if delay is None:
            delay = 0.0001
        
        self.bus = smbus.SMBus(port)
        self.addr = addr
        self.delay = functools.partial(asyncio.sleep, delay)

    async def write_byte(self, byte):
        self.bus.write_byte(self.addr, byte)
        await self.delay()

    async def write_byte_data(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        await self.delay()

    async def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        await self.delay()
    
    async def read(self):
        return self.bus.read_byte(self.addr)
    
    async def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)
    
    async def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)
