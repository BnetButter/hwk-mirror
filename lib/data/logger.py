from functools import wraps
from time import localtime, strftime
import logging
import sys


GUI_STDOUT = "gui.stdout"
GUI_STDERR = "gui.stderr"
SYS_STDOUT = "sys.stdout"
SYS_STDERR = "sys.stderr"

logging.getLogger(GUI_STDOUT).setLevel(logging.INFO)
logging.getLogger(GUI_STDERR).setLevel(logging.WARNING)

logging.getLogger(SYS_STDOUT).setLevel(logging.DEBUG)
logging.getLogger(SYS_STDERR).setLevel(logging.CRITICAL)


BLACK = "[{};30m"
RED = "[{};31m"
GREEN = "[{};32m"
YELLOW = "[{};33m"
BLUE = "[{};34m"
MAGENTA = "[{};35m"
CYAN = "[{};36m"
WHITE = "[{};37m"
ESC = "\033"
END = ESC + "[0m"

BOLD = 1
FAINT = 2
ITALIC = 3
UNDERLINE = 4


ASCIITIME = "%(asctime)s"
FUNC_NAME = "%(funcName)s"
LEVEL_NAME = "%(levelname)s"
LINE_NO = "%(lineno)s"
MESSAGE = "%(message)s"
NAME = "%(name)s"

def gettime():
    ct_local = localtime()
    return strftime("%m/%d/%y %I:%M:%S %p", ct_local)

def log_debug(message, name=SYS_STDOUT, time=False):
    logger=logging.getLogger(name)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if time:
                time = gettime() + " - "
            else:
                time = ""
            logger.debug(f"{time}{message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_info(message, name=GUI_STDOUT, time=False):
    logger = logging.getLogger(name)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if time:
                _time = gettime() + " - "
            else:
                _time = ""
            logger.info(f"{_time}{message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_warning(message, name=GUI_STDERR, time=False):
    logger = logging.getLogger(name)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _time = ""
            if time:
                _time = gettime() + " - "
            logger.warning(f"{_time}{message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def black(string, effect=1):
    return ESC + BLACK.format(effect) + string + END

def red(string, effect=1):
    return ESC + RED.format(effect) + string + END

def green(string, effect=1):
    return ESC + GREEN.format(effect) + string + END

def yellow(string, effect=1):
    return ESC + YELLOW.format(effect) + string + END

def blue(string, effect=1):
    return ESC + BLUE.format(effect) + string + END

def magenta(string, effect=1):
    return ESC + MAGENTA.format(effect) + string + END

def cyan(string, effect=1):
    return ESC + CYAN.format(effect) + string + END

def white(string, effect=1):
    return ESC + WHITE.format(effect) + string + END






