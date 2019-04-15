"""in-memory streams that interfaces with gui widgets"""

from io import StringIO
import tkinter as tk

class stringio(StringIO):
    """Seemless integration for logging and gui widgets"""

    methods = ["read", "write", "close"]

    @staticmethod
    def set(instance, other):
        """[instance]: an initiated stringio object.
        [other]: an instance of some class which defines alternative stringio.methods"""

        for name in stringio.methods:
            if hasattr(other, name):
                instance.__setattr__(name, other.__getattribute__(name))
            else:
                raise NotImplementedError(f"{other} is missing {name}")

    def read(self, *args):
        return self.getvalue()
    
    def __iter__(self):
        self.count = 0
        self.iterable = self.getvalue().split('\n')
        self.max = len(self.iterable)
        return self

    def __next__(self):
        if self.count > self.max - 1:
            raise StopIteration
        self.count += 1
        return self.iterable[self.count - 1]
    
    def __aiter__(self):
        self.count = 0
        self.iterable = self.getvalue().split('\n')
        self.max = len(self.iterable)
        return self
    
    async def __anext__(self):
        if self.count > self.max - 1:
            raise StopAsyncIteration
        self.count += 1
        return self.iterable[self.count - 1]



# default implementations.


def read(self):
    return StringIO.getvalue(type(self).stream)

def write(self, content, replace=0):
    self['state'] = tk.NORMAL
    if replace:
        self.delete(tk.END + f"-{replace}c", tk.END)
    self.insert(tk.END , content)
    self['state'] = tk.DISABLED
    self.see(tk.END)
    return StringIO.write(self.stream, content)

def close(self):
    type(self).stream.close()

def set_stream(self):
    for name in stringio.methods:
        if hasattr(self, name):
            self.stream.__setattr__(name, self.__getattribute__(name))
        else:
            raise NotImplementedError(f"{self} is missing {name}")

default_methods = {
    "read":read,
    "write":write, 
    "close":close}


stdout = stringio()
stderr = stringio()


class StreamType(type):

    def __new__(cls, name, bases, attr, stream=None, **kwargs):
        for method in stringio.methods:
            if method not in attr:
                attr[method] = default_methods[method]
        attr["set_stream"] = set_stream
        return super().__new__(cls, name, bases, attr, **kwargs)
    
    def __init__(self, name, bases, attr, stream=None, **kwags):
        if stream is None:
            stream = stdout
        self.stream = stream