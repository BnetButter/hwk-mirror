from distutils.core import setup, Extension

drawer_module = Extension("_cashdrawer", 
        sources=["drawermodule.c"],
        include_dirs=['/home/pi/.local/include/python3.7m'],
        libraries=["wiringPi"])

setup(ext_modules=[drawer_module])