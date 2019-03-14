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


ASCIITIME = "%(asciitime)s"
FUNC_NAME = "%(funcName)s"
LEVEL_NAME = "%(levelname)s"
LINE_NO = "%(lineno)s"
MESSAGE = "%(message)s"
NAME = "%(name)s"

LOGNAME_GUI_STDOUT = "gui.stdout"
LOGNAME_GUI_STDERR = "gui.stderr"


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






