import POS
import LineDisplay
import sys
import subprocess
import multiprocessing
import lib
import pos
import display
import server
import functools

# I would suggest following PEP8 to help organize your import statements.
# https://www.python.org/dev/peps/pep-0008/#imports
# In fact, you can install packages like pylint and flake8 that will do the work for you.
#
# Also consider not doing absolute imports for everything and just important the namespaces that are
# important to you.
# from subprocess import check_output, STDOUT, call
# from multiprocessing import Process

def kill_server(port=None):
    """kill program connected to port"""
    if port is None:
        port = 8080
    
    port = int(port)
    try:
        sub = subprocess.check_output(f"lsof -i:{port}", shell=True, stderr=subprocess.STDOUT)
        output = sub.decode().split("\n")
        ids = {line.split()[-1] for line in output if 'python' in line}
    except:
        ids = None
    finally:
        if ids:
            [subprocess.call(f"kill {ppid}", shell=True) for ppid in ids]
            print("done")  
        else:
            print(f"{port} is clear.")

def main():
    # See my general comments, but you are making this harder than it needs to be by using multiprocessing.Process and then abandoning those child processes. If you have a constantly running process to manage them, you can kill them with a multiprocessing.Event and use a queue to move messages between them.
    pos_process = multiprocessing.Process(target=pos.main, args=(POS.POSProtocol,))
    server_process = multiprocessing.Process(target=server.main)
    
    target0 = functools.partial(display.main, LineDisplay.CookLineProtocol, ncol=3, geometry="1920x1080")
    display0_process = multiprocessing.Process(target=target0)
    
    target1_protocol = functools.partial(LineDisplay.DrinkLineProtocol, exclude=["Bottled"])
    target1 = functools.partial(display.main, target1_protocol, ncol=2, geometry="1440x900")
    display1_process = multiprocessing.Process(target=target1)

    # argparse is the package that you want to use here.  I'd advise taking the time to learn it.i
    # It's an excellent tool to have in your toolbox.
    try:
        arg = sys.argv[1]
        if arg == "kill":
            return kill_server(lib.CONFIGDATA["port"])
        else:
            {"pos":pos_process,
            "server": server_process,
            "display0" : display0_process,
            "display1": display1_process}.get(sys.argv[1]).start()
    
    except IndexError:
        server_process.start()
        pos_process.start()
        display0_process.start()
        display1_process.start()



if __name__ == "__main__":
    main()
    



