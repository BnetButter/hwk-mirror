from lib import stdout
from lib import StreamType, new_stream
from lib.data import colors
import logging as log
import tkinter as tk
from POS import console_stdout
from POS import console_stderr
from POS import console_stdin
from lib import TabbedFrame
from POS import Console
from POS import MenuDisplay
stdout.write("writing to stdout...\n")
logger = log.getLogger(__name__)
logger.setLevel(log.INFO)
stream_handler = log.StreamHandler(stream=stdout)
logger.addHandler(stream_handler)

root = tk.Tk()
menu_display = MenuDisplay(root)
console = Console(root)
console.echo = stdout
stdout.write("hello\n")
console.grid(row=0, column=0)


logger.info("logger: INFO")
stdout.write("writing to widget\n")
root.mainloop()



