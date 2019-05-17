from distutils.core import setup, Extension


drawer_module = Extension("_cashdrawer", 
        sources=["drawermodule.c",
                 "./drawer.c"],
        include_dirs=['./drawermodule.h'],
        libraries=["wiringPi"])

setup(ext_modules=[drawer_module])