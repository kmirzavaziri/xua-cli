import os
from shutil import copyfile


class Logger:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'

    class Format:
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        LIGHT_GRAY = '\033[37m'
        DARK_GRAY = '\033[90m'
        LIGHT_RED = '\033[91m'
        LIGHT_GREEN = '\033[92m'
        LIGHT_YELLOW = '\033[93m'
        LIGHT_BLUE = '\033[94m'
        LIGHT_MAGENTA = '\033[95m'
        LIGHT_CYAN = '\033[96m'
        WHITE = '\033[97m'

        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

        @staticmethod
        def format(text, format):
            return format + text + Logger.Format.END

    @staticmethod
    def log(type, stack, message):
        typeText = f'{type: <7}'
        if (type == Logger.INFO):
            typeText = Logger.Format.format(
                typeText, Logger.Format.BOLD + Logger.Format.LIGHT_BLUE)
        elif (type == Logger.WARNING):
            typeText = Logger.Format.format(
                typeText, Logger.Format.BOLD + Logger.Format.LIGHT_YELLOW)
        elif (type == Logger.ERROR):
            typeText = Logger.Format.format(
                typeText, Logger.Format.BOLD + Logger.Format.LIGHT_RED)
        elif (type == Logger.SUCCESS):
            typeText = Logger.Format.format(
                typeText, Logger.Format.BOLD + Logger.Format.LIGHT_GREEN)

        stackText = f'{stack: <12}'
        stackText = Logger.Format.format(stackText, Logger.Format.MAGENTA)
        print(
            f'{typeText} {stackText} {Logger.Format.format(message, Logger.Format.LIGHT_GRAY)}')


def getNearestDirContaining(path, containing):
    if os.path.isfile(path):
        path = os.path.dirname(path)
    while True:
        if containing in os.listdir(path):
            return path
        if path == os.path.dirname(path):
            return None
        path = os.path.dirname(path)


def copy(source, destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    copyfile(source, destination)


def write(content, destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, 'w') as f:
        f.write(content)


def doesPathContainPath(parent, child):
    parent = os.path.abspath(parent)
    child = os.path.abspath(child)
    return os.path.commonpath([parent]) == os.path.commonpath([parent, child])
