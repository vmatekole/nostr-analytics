import logging
import os
import re
from logging import Logger

from dotenv import load_dotenv
from rich.logging import RichHandler


def init() -> Logger:
    load_dotenv()  # TODO: Remove
    level = os.environ.get('LOG_LEVEL', logging.DEBUG)
    level = getattr(logging, level, logging.DEBUG) if isinstance(level, str) else level
    logFormatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(processName)s %(message)s'
    )
    fileHandler = logging.FileHandler('./logs/debug5.log')
    richhandler: RichHandler = RichHandler(level)

    rootLogger = logging.getLogger()
    rootLogger.setLevel(level=level)
    for hdlr in [richhandler, fileHandler]:
        rootLogger.addHandler(hdlr)
        hdlr.setFormatter(logFormatter)
    return rootLogger


def normalise_string(query: str):
    return re.sub(r'[\s\t]+', '', query)


logger: Logger = init()
