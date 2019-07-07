#! /home/pi/.local/bin/python3.7
from connector import Connection
import pathlib
import os
import json



if __name__ == "__main__":
    confpath = os.path.join(str(pathlib.Path.home()),".hwk/config.json")
    with open(confpath, "r") as fp:
        config = json.load(fp)

    router_ip, port = config["router"], config["port"]
    config["ip"] = Connection(router_ip, port).result
    with open(confpath, "w") as fp:
       json.dump(config, fp, indent=4)

    import LineDisplay
    import display
    import sys

    if sys.argv[1] == "display0":
        display.main(LineDisplay.CookLineProtocol, 3)
    elif sys.argv[1] == "display1":
        display.main(LineDisplay.DrinkLineProtocol, 2)