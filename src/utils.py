import logging

from rich.logging import RichHandler

FORMAT = '%(message)s'
logging.basicConfig(
    level='NOTSET', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
)


def log(level: int):
    log = logging.getLogger('rich')
    log.setLevel(level)
    return logging
