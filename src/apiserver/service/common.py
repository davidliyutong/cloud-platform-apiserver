"""
This module describes the interface of a service.
"""

from abc import ABCMeta, abstractmethod
from typing import Optional, Any

from src.components.config import APIServerConfig


class ServiceInterface(metaclass=ABCMeta):
    """
    Service interface. All baisc services should inherit from this class.
    """
    parent: Optional['RootServiceInterface'] = None  # point to the parent service
    repo: Optional[Any] = None  # point to the repo


class RootServiceInterface(metaclass=ABCMeta):
    """
    Root interface. All services should inherit from this class.
    """
    opt: Optional[APIServerConfig] = None
    auth_service: ServiceInterface = None
    user_service: ServiceInterface = None
    template_service: ServiceInterface = None
    pod_service: ServiceInterface = None
    k8s_operator_service: ServiceInterface = None
    heartbeat_service: ServiceInterface = None
