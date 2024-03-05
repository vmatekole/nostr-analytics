import logging
from venv import logger

from rich.logging import RichHandler


class Logger:
    FORMAT = '%(message)s'
    logging.basicConfig(
        level='NOTSET', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
    )
    _file_handler = logging.FileHandler('logs/debug.log', mode='w')

    @staticmethod
    def log(level: int):
        Logger._file_handler.setLevel(
            logging.DEBUG
        )  # Set the level for the file handler
        log = logging.getLogger('rich')
        log.addHandler(Logger._file_handler)
        log.setLevel(level)
        return logging
