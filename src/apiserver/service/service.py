import dataclasses
from typing import Optional

from kubernetes import client

from .common import ServiceInterface
from .admin_user import AdminUserService
from .admin_template import AdminTemplateService
from .operator import K8SOperatorService
from ..repo import UserRepo, TemplateRepo


@dataclasses.dataclass
class RootService:
    auth_basic_service: ServiceInterface = None
    admin_user_service: AdminUserService = None
    admin_template_service: AdminTemplateService = None
    nonadmin_user_service: ServiceInterface = None
    nonadmin_pod_service: ServiceInterface = None
    k8s_operator_service: K8SOperatorService = None



_service: Optional[RootService] = None


def new_root_service(user_repo: UserRepo,
                     template_repo: TemplateRepo,
                     k8s_api: Optional[client.CoreV1Api] = None):
    global _service
    _service = RootService(
        auth_basic_service=ServiceInterface(),
        admin_user_service=AdminUserService(user_repo),
        admin_template_service=AdminTemplateService(template_repo),
        nonadmin_user_service=ServiceInterface(),
        nonadmin_pod_service=ServiceInterface(),
        k8s_operator_service=K8SOperatorService(k8s_api)
    )
    return _service


def get_root_service():
    global _service
    if _service is None:
        raise RuntimeError("root service not initialized")
    return _service
