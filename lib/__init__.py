from .metaclass import *
from .tkasync import *
from .data import *
from .ticket import *
from .tkwidgets import *
from .stream import stdin, stderr, stdout
from .stream import StreamType
from .stream import new_stream
from .event_manager import EventManager
import logging

# loggers targeting the gui output widget



stdout_logger = logging.getLogger(LOGNAME_GUI_STDOUT)
stdout_logger.setLevel(logging.INFO)
stderr_logger = logging.getLogger(LOGNAME_GUI_STDERR)
stderr_logger.setLevel(logging.WARNING)

gui_stdout = logging.StreamHandler(stream=stdout)
gui_stdout.setLevel(logging.INFO)

gui_stderr = logging.StreamHandler(stream=stderr)
gui_stderr.setLevel(logging.WARNING)

stdout_logger.addHandler(gui_stdout)
stderr_logger.addHandler(gui_stderr)
