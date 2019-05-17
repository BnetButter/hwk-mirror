import lib
import printer


port = "/dev/null" if lib.DEBUG else "/dev/serial0"

def Printer(*args):
    result = printer.new()
    result.__init__(port)
    return result

