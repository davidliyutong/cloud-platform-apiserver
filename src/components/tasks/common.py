import abc
import multiprocessing
from typing import Optional, Tuple

import sanic
from loguru import logger

from src.components.config import APIServerConfig


class AsyncTask(abc.ABC):
    def __init__(self, opt: APIServerConfig, sem: multiprocessing.BoundedSemaphore = None):
        self.opt = opt
        self.sem = sem

    @abc.abstractmethod
    async def loop(self, app: sanic.Sanic) -> Tuple[bool, Optional[Exception]]:
        raise NotImplementedError

    async def __call__(self, app: sanic.Sanic):
        if self.sem is not None:
            # logger.info(f"try to start task {self.__class__.__name__} at pid {multiprocessing.current_process().pid}")
            with self.sem:
                logger.info(f"start task {self.__class__.__name__} at pid {multiprocessing.current_process().pid}")
                res = await self.loop(app)
                logger.info(f"end task {self.__class__.__name__} at pid {multiprocessing.current_process().pid}")
                return res
        else:
            return await self.loop(app)
