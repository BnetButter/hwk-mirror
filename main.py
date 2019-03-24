import logging
import sys
import subprocess
import multiprocessing
import lib
import pos
import display
import server

from POS import POSProtocol


def kill_server(port=None):
    """kill program connected to port"""
    if port is None:
        port = 8080
    
    port = int(port)
    try:
        sub = subprocess.check_output(f"lsof -i:{port}", shell=True, stderr=subprocess.STDOUT)
        output = sub.decode().split("\n")
        lines = list()
        ids = set()
        for line in output:
            if "python" in line:
                lines.append(line)
        
        for line in lines:
            ids.add(line.split()[1])
    except:
        ids = None
    finally:
        if ids is not None and ids != {}:
            [subprocess.call(f"kill {ppid}", shell=True) for ppid in ids]
            print("done")  
        else:
            print(f"{port} is clear.")

from POS import POSProtocol
import functools

switch = {
    "pos": functools.partial(pos.main, POSProtocol),
    "server": server.main,
    "display": display.main
}

def process(arg):
    result = switch.get(arg)
    result()

def main():
    try:
        arg = sys.argv[1]
        if arg == "kill":
            kill_server(lib.CONFIGDATA["port"])
        else:
            result = switch.get(arg, lambda: print(f"invalid argument {arg}"))
            result()

    except IndexError:
        pool = multiprocessing.Pool(3)
        pool.map(process, ["pos", "server", "display"])


if __name__ == "__main__":
    main()


