"""
This module contains all the utility functions.
"""

import base64
import secrets
import signal
from functools import wraps

from loguru import logger


def singleton(cls):
    """
    Singleton decorator. Make sure only one instance of cls is created.

    :param cls: cls
    :return: instance
    """
    _instances = {}

    @wraps(cls)
    def instance(*args, **kw):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kw)
        return _instances[cls]

    return instance


class DelayedKeyboardInterrupt:
    """
    Shield code from KeyboardInterrupt
    """
    signal_received = None

    def __enter__(self):
        self.signal_received = None
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logger.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


def random_password(length: int = 16) -> str:
    """
    Generate random password
    """
    return base64.encodebytes(secrets.token_bytes(length))[:length].decode('utf-8')


