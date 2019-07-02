from setuptools import setup, find_packages


setup(name="hwk-system",
    version="2.0a",
    packages=find_packages(),
    description="integrated pos system",
    author="Ziyu (Kevin) Lai",
    install_requires=["websockets", "SMBus"])