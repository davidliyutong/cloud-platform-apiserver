from abc import ABCMeta
from typing import Optional
import dataclasses


class ServiceInterface(metaclass=ABCMeta):
    parent: Optional['ServiceInterface'] = None
    auth_basic_service: Optional['ServiceInterface'] = None
    admin_user_service: Optional['ServiceInterface'] = None
    admin_template_service: Optional['ServiceInterface'] = None
    nonadmin_user_service: Optional['ServiceInterface'] = None
    nonadmin_pod_service: Optional['ServiceInterface'] = None
    k8s_operator_service: Optional['ServiceInterface'] = None