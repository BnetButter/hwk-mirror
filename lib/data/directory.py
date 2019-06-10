from pathlib import Path
import os

APPDATA = os.path.join(str(Path.home()), ".hwk")

if not os.path.exists(APPDATA):
    os.mkdir(APPDATA)

MENUPATH = os.path.join(APPDATA, "menu_items.json")
LOGPATH = os.path.join(APPDATA, "server.log")
CONFIGPATH = os.path.join(APPDATA, "config.json")
SALESLOG = os.path.join(APPDATA, "sales.csv")
