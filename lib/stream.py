"""in-memory streams that interfaces with gui widgets"""

from io import StringIO
import tkinter as tk

class stringio(StringIO):
    """Seemless integration for logging and gui widgets"""

    methods = ["read", "write", "__iter__", "close"]

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

# default implementations.
def __iter__(self):
    for line in StringIO.getvalue(type(self).stream).split('\n'):
        yield line

def read(self):
    return StringIO.getvalue(type(self).stream)

def write(self, content):
    self['state'] = tk.NORMAL
    self.insert(tk.END, content)
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
    "__iter__":__iter__, 
    "read":read,
    "write":write, 
    "close":close
    }

stdin = stringio()
stdout = stringio()
stderr = stringio()
new_stream = stringio.set

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
    
