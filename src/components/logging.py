"""
This module contains all logging related functions.
"""
import logging
import os
import os.path as osp
import sys
from datetime import timedelta, datetime, time
from typing import Set

from loguru import logger


class Rotator:
    """
    Rotator is a class that can be used to rotate log files.
    """

    def __init__(self, *, size, at):
        now = datetime.now()
        self._size_limit = size
        self._time_limit = now.replace(hour=at.hour, minute=at.minute, second=at.second)

        if now >= self._time_limit:
            self._time_limit += timedelta(days=1)

    def should_rotate(self, message, file):
        file.seek(0, 2)
        if file.tell() + len(message) > self._size_limit:
            return True
        if message.record["time"].timestamp() > self._time_limit.timestamp():
            self._time_limit += timedelta(days=1)
            return True
        return False


LOGGER_LVL_SET: Set[str] = {'info', 'debug', 'error', 'warning'}


def create_log_file(log_root, lvl):
    """
    Create a log file with the given level.s
    """
    if not osp.exists(log_root):
        os.makedirs(log_root, exist_ok=True)
    path_to_log = f"{log_root}/{lvl}.log"
    f = open(path_to_log, "a+")
    f.close()
    return path_to_log


class InterceptHandler(logging.Handler):
    """
    InterceptHandler is a class that can be used to intercept log messages and redirect them to loguru.
    """

    def __init__(self, level=logging.INFO):
        super().__init__(level)

    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


# 修改 create_logger
def create_logger(log_root: str = "./logs", debug: bool = False):
    """
    Create and configure project level logger
    """
    # supress kubernetes logs
    if not debug:
        logging.getLogger("kubernetes").setLevel(logging.WARNING)
        logging.getLogger("kubernetes").propagate = False
    else:
        pass

    # replace sanic logger with loguru
    logging.getLogger("sanic.root").handlers.clear()
    logging.getLogger("sanic.server").handlers.clear()
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # rotate file if over 500 MB or at midnight every day
    rotator = Rotator(size=5e+8, at=time(0, 0, 0))

    # remove default logger and add stderr logger
    logger.remove()
    if not debug:
        logger.add(sys.stderr, level="INFO")
    else:
        logger.add(sys.stderr, level="DEBUG")

    # add file loggers
    if not debug:
        s = set([x for x in list(LOGGER_LVL_SET) if x != 'debug'])
    else:
        s = LOGGER_LVL_SET
    for lvl in s:
        logger.add(create_log_file(log_root, lvl), rotation=rotator.should_rotate, level=lvl.upper())

    return logger
