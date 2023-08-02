"""
This module describes the interface of a service.
"""

from abc import ABCMeta
from typing import Optional

from src.components.config import APIServerConfig


class ServiceInterface(metaclass=ABCMeta):
    """
    Service interface. All services should inherit from this class.
    """
    opt: Optional[APIServerConfig] = None
    parent: Optional['ServiceInterface'] = None  # point to the parent service
