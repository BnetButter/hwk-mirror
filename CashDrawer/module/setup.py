from distutils.core import setup, Extension


drawer_module = Extension("_cashdrawer", 
        sources=["drawermodule.c",
                 "./drawer.c"],
        include_dirs=['./drawer.h'])

setup(ext_modules=[drawer_module])