from .configurations import *
from .menu_items import *
from .directory import *
from json import dump
from json import load
from .logger import *
from .salesinfo import *

try:
    with open(MENUPATH, "r") as fp:
        MENUDATA = load(fp)
except:
    with open(MENUPATH, "w") as fp:
        dump(DEFAULT_MENU, fp, indent=4)
    MENUDATA = DEFAULT_MENU

try:
    with open(CONFIGPATH, "r") as fp:
        CONFIGDATA = load(fp)
except:
    with open(CONFIGPATH, "w") as fp:
        dump(DEFAULT_MENU, fp, indent=4)
    CONFIGDATA = DEFAULT_MENU


router_ip = CONFIGDATA["router"]
device_ip = CONFIGDATA["ip"] # ip address of the RPI running the server process
port = CONFIGDATA["port"] # port of the primary server handler
DEBUG = CONFIGDATA["__debug"]
address = f"ws://{device_ip}:{port}"


class _TicketStatus(int):
    
    def __new__(cls, number):
        return super().__new__(cls, number)

    def __str__(self):
        if self == -1:
            return "Queued"
        elif self == 0:
            return "Processing"
        elif self == 1:
            return "Complete"
    
    

TICKET_QUEUED = _TicketStatus(-1)
TICKET_WORKING = _TicketStatus(0)
TICKET_COMPLETE = _TicketStatus(1)
