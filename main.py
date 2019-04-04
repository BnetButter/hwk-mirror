import logging
import sys
import subprocess
import multiprocessing
import lib
import pos
import display
import server

from POS import POSProtocol, POSProtocolBase

# TODO make delegate responsible for calculating total. 
# adjust "OrderInterface" class accordingly

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

def main():

    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(name)s - %(message)s"))
    logger.addHandler(handler)
    
    logger.info("starting main")


    pos_process = multiprocessing.Process(target=pos.main, args=(POSProtocol,))
    server_process = multiprocessing.Process(target=server.main)
    try:
        arg = sys.argv[1]
        if arg == "kill":
            return kill_server(lib.CONFIGDATA["port"])
        else:
            {"pos":pos_process, "server": server_process}.get(sys.argv[1]).start()
    
    except IndexError:
        server_process.start()
        pos_process.start()
    
if __name__ == "__main__":
    main()