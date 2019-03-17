from setuptools import setup

packages = ["POS", "Display", "Server"]

setup(name="hwk-system",
    version="2.0a",
    packages=packages,
    description="integrated pos system",
    author="Ziyu (Kevin) Lai",
    install_requires=["websockets"])