import datetime
import uuid
from enum import Enum
from typing import Optional, Union, Dict, Any, Self

import kubernetes
import shortuuid
from odmantic import Field, Model
from pydantic import BaseModel, UUID4, field_validator, field_serializer

from src import CONFIG_BUILD_VERSION
from src.components.config import CONFIG_K8S_POD_LABEL_FMT, CONFIG_K8S_CREDENTIAL_FMT
from .common import ResourceStatusEnum
from .quota import QuotaModelV2


class PodStatusEnum(str, Enum):
    """
    Pod status enum, used to define pod status.
    """
    pending = "pending"  # current
    creating = "creating"  # current (unused)
    running = "running"  # current | target
    stopped = "stopped"  # current | target
    deleting = "deleting"  # current (unused)
    failed = "failed"  # current
    unknown = "unknown"  # current

    @classmethod
    def from_k8s_status(cls, ret_status: kubernetes.client.models.v1_deployment_status.V1DeploymentStatus):
        if ret_status.replicas is None:
            if ret_status.ready_replicas is None:
                return cls.stopped
            else:
                return cls.pending
        else:
            if ret_status.ready_replicas is None:
                return cls.pending
            else:
                return cls.running


class PodModelV1(BaseModel):
    """
    Pod model, used to define pod
    """
    version: str
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    pod_id: str
    name: str
    description: str
    template_ref: UUID4
    template_str: Optional[str]
    cpu_lim_m_cpu: int
    mem_lim_mb: int
    storage_lim_mb: int
    username: str
    user_uuid: UUID4
    created_at: datetime.datetime
    started_at: datetime.datetime
    accessed_at: datetime.datetime
    timeout_s: int
    current_status: PodStatusEnum
    target_status: PodStatusEnum

    @field_validator("version")
    def version_must_be_valid(cls, v):
        if v is None or v == "":
            v = CONFIG_BUILD_VERSION
        return v

    @field_serializer('template_ref')
    def serialize_uuid(self, v: uuid.UUID, _info):
        return str(v)

    @field_validator('created_at')
    def validate_created_at(cls, v: Union[str, datetime.datetime]):
        if isinstance(v, str):
            v = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
        return v

    @field_serializer('user_uuid')
    def serialize_user_uuid(self, v: uuid.UUID, _info):
        return str(v)

    @field_serializer('created_at')
    def serialize_created_at(self, v: datetime.datetime, _info):
        return v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @field_validator('started_at')
    def validate_started_at(cls, v: Union[str, datetime.datetime]):
        if isinstance(v, str):
            v = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
        return v

    @field_serializer('started_at')
    def serialize_started_at(self, v: datetime.datetime, _info):
        return v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @field_validator('accessed_at')
    def validate_accessed_at(cls, v: Union[str, datetime.datetime]):
        if isinstance(v, str):
            v = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
        return v

    @field_serializer('accessed_at')
    def serialize_accessed_at(self, v: datetime.datetime, _info):
        return v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def values(self):
        """
        values used to render template
        """

        return {
            "POD_LABEL": CONFIG_K8S_POD_LABEL_FMT.format(self.pod_id),
            "POD_ID": self.pod_id,
            "POD_CPU_LIM": str(self.cpu_lim_m_cpu) + "m",
            "POD_MEM_LIM": str(self.mem_lim_mb) + "Mi",
            "POD_STORAGE_LIM": str(self.storage_lim_mb) + "Mi",
            "POD_AUTH": CONFIG_K8S_CREDENTIAL_FMT.format(str(self.user_uuid)),
            "POD_USERNAME": self.username,
            "POD_REPLICAS": "1" if self.target_status == PodStatusEnum.running else "0",
        }

    @classmethod
    def new(cls,
            template_ref: Optional[str],
            username: str,
            user_uuid: str,
            name: str = "",
            description: str = "",
            cpu_lim_m_cpu: int = 1000,
            mem_lim_mb: int = 512,
            storage_lim_mb: int = 10240,
            timeout_s: int = 3600):
        return cls(
            version=CONFIG_BUILD_VERSION,
            pod_id=shortuuid.uuid(),
            name=name,
            description=description,
            template_ref=uuid.UUID(template_ref),
            template_str=None,
            cpu_lim_m_cpu=cpu_lim_m_cpu,
            mem_lim_mb=mem_lim_mb,
            storage_lim_mb=storage_lim_mb,
            username=username,
            user_uuid=uuid.UUID(user_uuid),
            created_at=datetime.datetime.utcnow(),
            started_at=datetime.datetime.fromtimestamp(0),
            accessed_at=datetime.datetime.fromtimestamp(0),
            timeout_s=timeout_s,
            current_status=PodStatusEnum.pending,
            target_status=PodStatusEnum.running,
        )

    @classmethod
    def upgrade(cls, d: Dict[str, Any]) -> Self:
        res = cls(**d)
        res.version = CONFIG_BUILD_VERSION
        return res


class PodModelV2(Model):
    """
    Pod model v2, used to define pod
    """
    model_config = {
        "collection": "pods",
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.pending, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    pod_id: str = Field(index=True, primary_field=True, default_factory=shortuuid.uuid)
    name: str = Field(default="")
    description: str = Field(default="")
    template_ref: str = Field()
    template_cache: Optional[Dict[str, Any]] = Field(default=None)
    quota: QuotaModelV2 = Field()
    owner_username: str = Field()
    owner_uuid: str = Field()
    started_at: datetime.datetime = Field()
    accessed_at: datetime.datetime = Field()
    current_status: PodStatusEnum = Field()
    target_status: PodStatusEnum = Field()
