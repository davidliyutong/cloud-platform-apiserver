from typing import Optional

from kubernetes import client

from .common import ServiceInterface


class K8SOperatorService(ServiceInterface):
    def __init__(self, v1: Optional[client.CoreV1Api]):
        super().__init__()
        self.v1 = v1
