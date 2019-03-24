from .configurations import *
from .menu_items import *
from .directory import *
from json import dump
from json import load
from .logger import *

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
device_ip = CONFIGDATA["ip"]
port = CONFIGDATA["port"]
address = f"ws://{device_ip}:{port}"
