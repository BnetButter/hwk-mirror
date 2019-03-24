from .metaclass import *
from .data import *
from .tkwidgets import *
from .stream import *
from .tkinterface import *
from .abstract import *
from .globalstate import GlobalState
import logging

# loggers targeting the gui output widget
logging.getLogger(GUI_STDOUT
        ).addHandler(logging.StreamHandler(
                stream=stdout))

logging.getLogger(GUI_STDERR
        ).addHandler(logging.StreamHandler(
                stream=stderr))
