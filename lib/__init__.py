from .metaclass import *
from .data import *
from .ticket import *
from .tkwidgets import *
from .stream import *
from .abstractserver import *
from .event_manager import Event
import logging

# loggers targeting the gui output widget
logging.getLogger(GUI_STDOUT
        ).addHandler(logging.StreamHandler(
                stream=stdout))

logging.getLogger(GUI_STDERR
        ).addHandler(logging.StreamHandler(
                stream=stderr))