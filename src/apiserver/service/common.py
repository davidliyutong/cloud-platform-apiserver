from abc import ABCMeta
from typing import Optional


class ServiceInterface(metaclass=ABCMeta):
    parent: Optional['ServiceInterface'] = None
    auth_basic_service: Optional['ServiceInterface'] = None
    user_service: Optional['ServiceInterface'] = None
    template_service: Optional['ServiceInterface'] = None
    pod_service: Optional['ServiceInterface'] = None
    k8s_operator_service: Optional['ServiceInterface'] = None