from datetime import timedelta, datetime, time
from typing import Set
from loguru import logger
import os.path as osp
import os
import logging

class Rotator:
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
    if not osp.exists(log_root):
        os.makedirs(log_root, exist_ok=True)
    path_to_log = f"{log_root}/{lvl}.log"
    f = open(path_to_log, "a+")
    f.close()
    return path_to_log


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


# 修改 create_logger
def create_logger(log_root: str = "./logs"):
    # ----------------- 添加这两行，替换 Sanic 默认 logger 配置
    logging.getLogger("sanic.root").handlers.clear()
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Rotate file if over 500 MB or at midnight every day
    rotator = Rotator(size=5e+8, at=time(0, 0, 0))

    for lvl in LOGGER_LVL_SET:
        logger.add(create_log_file(log_root, lvl), rotation=rotator.should_rotate, level=lvl.upper())

    return logger
