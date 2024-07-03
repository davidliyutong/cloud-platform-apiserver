"""
This module describes the interface of a service.
"""
from abc import ABCMeta
from typing import Optional, Any

from odmantic import AIOEngine


class ServiceInterface(metaclass=ABCMeta):
    """
    Service interface. All baisc services should inherit from this class.
    """
    repo: Optional[Any] = None  # point to the repo
    _engine: Optional[AIOEngine]
    _root_service: Optional['RootService']

    @property
    def valid(self) -> bool:
        return self._engine is not None

    @property
    def root_service(self):
        return self._root_service

    @root_service.setter
    def root_service(self, root_service: 'RootService'):
        self._root_service = root_service
