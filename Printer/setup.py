from distutils.core import setup, Extension

printer_module = Extension("printer", 
        sources=["printermodule.c",
                 "./adafruit/printer.c"],
        include_dirs=['./adafruit/include',
        	"/home/pi/.local/include/python3.7m"])

setup(ext_modules=[printer_module])