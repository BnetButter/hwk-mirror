from .i2c import AsyncSMBus
import math
import asyncio
import lib
import tkinter as tk

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

NROW = 4
NCOL = 20


if lib.DEBUG:
    class LCDScreen(tk.Tk, metaclass=lib.ToplevelWidget, device="POS"):
        font=()
        loop = asyncio.get_event_loop()

        def __init__(self, *args, **kwargs):
            super().__init__()
            self.wm_title("LCDScreen")
            frame = tk.Frame(self, bd=5, bg="black", relief=tk.SUNKEN)
            self._screen = [
                _Entry(frame, 
                    width=20, 
                    state=tk.DISABLED,
                    disabledforeground="white",
                    disabledbackground="blue",
                    bd=0,
                    font=("Monospace", 14),
                    highlightthickness=0)
                for i in range(4)
            ]
            self.resizable(0,0)
            self.last_total = None
            
            for i, entry in enumerate(self._screen):
                entry.grid(row=i, column=0, sticky="nswe")
            frame.grid(sticky="nswe")
            
            async def __init__():
                await self.display(" Total: $ 0.00", row=1)
                await self.display("  Cash: - - -", row=2)
                await self.display("Change: - - -", row=3)
            asyncio.run(__init__())
        
        async def set_ticket_no(self, value, postfix=""):
            if value is None:
                value = 1
            await self.display("        {:03d} {}".format(value, postfix))

        async def set_total(self, value):
            if value is None:
                return await self.display(" Total: - - -", row=1)
            await self.display(" Total: $ {:.2f}".format(value/100), row=1)
        
        async def set_cash(self, value):
            if value is None:
                return await self.display("  Cash: - - -", row=2)
            await self.display("  Cash: $ {:.2f}".format(value/100), row=2)
        async def set_change(self, value):
            if value is None:
                return await self.display("Change: - - -", row=3)
            await self.display("Change: $ {:.2f}".format(value / 100), row=3)

        async def display(self, text, row=0, col=0):
            entry = self._screen[row]
            entry.set((" " * col) + text)
        
        async def reset(self):
            for entry in self._screen:
                entry.set("")


    class _Entry(tk.Entry):

        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self._var = tk.StringVar(parent)
            self.configure(textvariable=self._var)

        def get(self):
            return self._var.get()
        
        def set(self, value):
            self._var.set(value)


else:
    class LCDScreen(AsyncSMBus, metaclass=lib.SingletonType):
        #initializes objects and lcd
        def __init__(self, addr=None, port=None, horizontal_refresh_rate=None):

            if addr is None:
                addr = 0x27 # check with i2cdetect

            if port is None:
                port = 1    # depends on pin and rpi rev.
            
            if horizontal_refresh_rate is None:
                horizontal_refresh_rate = 20000 # per sec
            super().__init__(addr, port, 1 / horizontal_refresh_rate)
            self.loop = asyncio.get_event_loop()
            async def init():
                await self.write_cmd(0x03)
                await self.write_cmd(0x03)
                await self.write_cmd(0x03)
                await self.write_cmd(0x02)

                await self.write_cmd(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
                await self.write_cmd(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
                await self.write_cmd(LCD_CLEARDISPLAY)
                await self.write_cmd(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
                await asyncio.sleep(0.2)

                await self.display(" Total: - - -", row=1)
                await self.display("  Cash: - - -", row=2)
                await self.display("Change: - - -", row=3)
            
            self.column = 8
            self.loop.run_until_complete(init())

        async def strobe(self, data):
            await super().write_byte(data | En | LCD_BACKLIGHT)
            await super().write_byte(((data & ~En) | LCD_BACKLIGHT))
        
        async def write_byte(self, data):
            await super().write_byte(data | LCD_BACKLIGHT)
            await self.strobe(data)

        async def write_cmd(self, cmd, mode=0):
            await self.write_byte(mode | (cmd & 0xF0))
            await self.write_byte(mode | ((cmd << 4) & 0xF0))

        async def writechar(self, charvalue, mode=1):
            await self.write_byte(mode | (charvalue & 0xF0))
            await self.write_byte(mode | ((charvalue << 4) & 0xF0))
        
        async def display(self, text, row=0, col=0):
            if row == 1:
                pos = 0x40 + col
            elif row == 2:
                pos = 0x14 + col
            elif row == 3:
                pos = 0x54 + col
            else:
                pos = col
            await self.write_cmd(0x80 + pos)
            for c in text:
                await self.write_cmd(ord(c), mode=Rs)
            
        async def reset(self):
            await self.write_cmd(LCD_CLEARDISPLAY)
            await self.write_cmd(LCD_RETURNHOME)
            await asyncio.sleep(0.2)

        def _getvalue(self, value):
            if value is None:
                string = "- - -"
            else:
                string = "$ {:.2f}".format(value / 100)
            # clear out rest of columns
            # otherwise trailing digits will remain on screen
            postfix = (NCOL - 1 - (len(string) + (self.column - 1))) * " "
            string = string + postfix
            assert self.column + len(string) == NCOL
            return string

        async def set_total(self, value):
            await self.display(self._getvalue(value), row=1, col=self.column)
        
        async def set_cash(self, value):
            await self.display(self._getvalue(value), row=2, col=self.column)
        
        async def set_change(self, value):
            await self.display(self._getvalue(value), row=3, col=self.column)
        
        async def set_ticket_no(self, value, postfix=""):
            if value is None:
                value = "*** " + postfix
            else:
                value = "{:03d} ".format(value) + postfix
            # clear out rest of the columns
            value += (NCOL - 1 - (len(value) + (self.column - 1))) * " "
            assert self.column + len(value) == NCOL

            await self.display(value, col=self.column)

