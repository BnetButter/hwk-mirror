from distutils.core import setup, Extension

printer_module = Extension("printer", 
        sources=["printermodule.c",
                 "./adafruit/printer.c"],
        include_dirs=['./adafruit/include'])

setup(ext_modules=[printer_module])