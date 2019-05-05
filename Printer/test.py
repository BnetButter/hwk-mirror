import printer

p = printer.new()
p.__init__("/dev/serial0")


# justify
CENTER = bytes("C", "utf-8")
RIGHT = bytes("R", "utf-8")

# size
MEDIUM = bytes("M", "utf-8")
LARGE = bytes("L", "utf-8")

p.writeline("test")
p.writeline("center justify", justify=CENTER)
p.writeline("right justify", justify=RIGHT)
p.writeline("large", size=LARGE)
p.writeline("medium", size=MEDIUM)
p.writeline("test", justify=CENTER, size=LARGE)
