import dataclasses
from typing import Optional

from kubernetes import client

from .common import ServiceInterface
from .user import UserService
from .template import TemplateService
from .pod import PodService
from .operator import K8SOperatorService
from .heartbeat import HeartbeatService
from src.apiserver.repo import UserRepo, TemplateRepo, PodRepo
from src.components.config import BackendConfig


@dataclasses.dataclass
class RootService(ServiceInterface):
    opt: BackendConfig
    auth_basic_service: ServiceInterface = None
    user_service: UserService = None
    template_service: TemplateService = None
    pod_service: PodService = None
    k8s_operator_service: K8SOperatorService = None
    heartbeat_service: HeartbeatService = None

    def __post_init__(self):
        if self.auth_basic_service is not None:
            self.auth_basic_service.parent = self

        if self.user_service is not None:
            self.user_service.parent = self

        if self.template_service is not None:
            self.template_service.parent = self

        if self.pod_service is not None:
            self.pod_service.parent = self

        if self.k8s_operator_service is not None:
            self.k8s_operator_service.parent = self

        if self.heartbeat_service is not None:
            self.heartbeat_service.parent = self


_service: Optional[RootService] = None


def new_root_service(opt: BackendConfig,
                     user_repo: UserRepo,
                     template_repo: TemplateRepo,
                     pod_repo: PodRepo,
                     k8s_client: Optional[client] = None):
    global _service
    _service = RootService(
        opt=opt,
        auth_basic_service=ServiceInterface(),
        user_service=UserService(user_repo),
        template_service=TemplateService(template_repo),
        pod_service=PodService(pod_repo),
        k8s_operator_service=K8SOperatorService(k8s_client),
        heartbeat_service=HeartbeatService(),
    )
    return _service


def get_root_service():
    global _service
    if _service is None:
        raise RuntimeError("root service not initialized")
    return _service
