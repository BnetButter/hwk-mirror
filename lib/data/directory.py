from pathlib import Path
import os

APPDATA = os.path.join(str(Path.home()), ".hwk")
MENUPATH = os.path.join(APPDATA, "menu_items.json")
LOGPATH = os.path.join(APPDATA, "server.log")
CONFIGPATH = os.path.join(APPDATA, "config.json")