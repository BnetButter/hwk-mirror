import lib

if not lib.DEBUG:
    import printer
    def Printer(*args):
        result = printer.new()
        result.__init__("/dev/serial0")
        return result

else:
    class Printer:

        def writeline(self, *args, **kwargs):
            ...
