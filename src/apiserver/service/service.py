import dataclasses
from typing import Optional

from kubernetes import client

from .common import ServiceInterface
from .user import AdminUserService
from .template import AdminTemplateService
from .pod import AdminPodService
from .operator import K8SOperatorService
from ..repo import UserRepo, TemplateRepo, PodRepo


@dataclasses.dataclass
class RootService(ServiceInterface):
    auth_basic_service: ServiceInterface = None
    user_service: AdminUserService = None
    template_service: AdminTemplateService = None
    pod_service: AdminPodService = None
    k8s_operator_service: K8SOperatorService = None

    def __post_init__(self):
        if self.auth_basic_service is not None:
            self.auth_basic_service.parent = self

        if self.user_service is not None:
            self.user_service.parent = self

        if self.template_service is not None:
            self.template_service.parent = self

        if self.pod_service is not None:
            self.pod_service.parent = self


_service: Optional[RootService] = None


def new_root_service(user_repo: UserRepo,
                     template_repo: TemplateRepo,
                     pod_repo: PodRepo,
                     k8s_api: Optional[client.CoreV1Api] = None):
    global _service
    _service = RootService(
        auth_basic_service=ServiceInterface(),
        user_service=AdminUserService(user_repo),
        template_service=AdminTemplateService(template_repo),
        pod_service=AdminPodService(pod_repo),
        k8s_operator_service=K8SOperatorService(k8s_api)
    )
    return _service


def get_root_service():
    global _service
    if _service is None:
        raise RuntimeError("root service not initialized")
    return _service
