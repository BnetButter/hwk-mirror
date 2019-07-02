#! /home/pi/.local/bin/python3.7
import multiprocessing
from pathlib import Path
import subprocess
import json
import os



if __name__ == "__main__":
    hostname = subprocess.Popen(("hostname", "-I"), stdout=subprocess.PIPE)
    my_ip = subprocess.check_output(("awk", "{{print $1}}"), stdin=hostname.stdout)
    hostname.wait()
    my_ip = my_ip.decode("utf-8").strip()

    configpath = os.path.join(str(Path.home()), ".hwk", "config.json")
    assert os.path.exists(configpath)

    with open(configpath, "r") as fp:
        conf = json.load(fp)
        conf["ip"] = my_ip

    with open(configpath, "w") as fp:
        json.dump(conf, fp, indent=4)
    
    import POS
    import Server
    import pos
    import server
    pos = multiprocessing.Process(target=pos.main, args=(POS.POSProtocol,))
    server = multiprocessing.Process(target=server.main)
    server.start()
    pos.start()