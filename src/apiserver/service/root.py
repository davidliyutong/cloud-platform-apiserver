"""
This module describes the interface of a service.
"""
from typing import Optional

from kubernetes import client
from odmantic import AIOEngine

from src.components.config import APIServerConfig
from src.components.utils import singleton
from .auth import AuthService
from .cluster import K8SOperatorService
from .group import GroupService
from .heartbeat import HeartbeatService
from .pod import PodService
from .policy import PolicyService
from .system import SystemService
from .template import TemplateService
from .user import UserService
from .volume import VolumeService


@singleton
class RootService():
    opt: APIServerConfig
    auth_service: AuthService = None
    k8s_operator_service: K8SOperatorService = None
    group_service: GroupService = None
    heartbeat_service: HeartbeatService = None
    pod_service: PodService = None
    system_service: SystemService = None
    template_service: TemplateService = None
    user_service: UserService = None
    volume_service: VolumeService = None
    policy_service: PolicyService = None

    def __init__(
            self,
            opt: APIServerConfig,
            auth_service: AuthService = None,
            k8s_operator_service: K8SOperatorService = None,
            group_service: GroupService = None,
            heartbeat_service: HeartbeatService = None,
            pod_service: PodService = None,
            system_service: SystemService = None,
            template_service: TemplateService = None,
            user_service: UserService = None,
            volume_service: VolumeService = None,
            policy_service: PolicyService = None
    ):
        self.opt = opt
        self.auth_service = auth_service
        self.auth_service.root_service = self

        self.k8s_operator_service = k8s_operator_service
        self.k8s_operator_service.root_service = self

        self.group_service = group_service
        self.group_service.root_service = self

        self.heartbeat_service = heartbeat_service
        self.heartbeat_service.root_service = self

        self.pod_service = pod_service
        self.pod_service.root_service = self

        self.system_service = system_service
        self.system_service.root_service = self

        self.template_service = template_service
        self.template_service.root_service = self

        self.user_service = user_service
        self.user_service.root_service = self

        self.volume_service = volume_service
        self.volume_service.root_service = self

        self.policy_service = policy_service
        self.policy_service.root_service = self


def init_root_service(opt: APIServerConfig,
                      odm_engine: AIOEngine,
                      k8s_client: Optional[client] = None):
    _ = RootService(
        opt=opt,
        auth_service=AuthService(odm_engine),
        k8s_operator_service=K8SOperatorService(k8s_client, opt.k8s_namespace),
        group_service=GroupService(odm_engine),
        heartbeat_service=HeartbeatService(),
        pod_service=PodService(odm_engine),
        system_service=SystemService(odm_engine),
        template_service=TemplateService(odm_engine),
        user_service=UserService(odm_engine),
        volume_service=VolumeService(odm_engine),
        policy_service=PolicyService(odm_engine)
    )
    return RootService()
