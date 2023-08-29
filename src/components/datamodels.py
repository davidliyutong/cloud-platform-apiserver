"""
Data models for the project
"""

import datetime
import uuid
from enum import Enum
from hashlib import sha256
from typing import List, Optional, Dict, Any, Union, Self

import bcrypt
import kubernetes
import shortuuid
from pydantic import BaseModel, UUID4, EmailStr, SecretStr
from pydantic import field_validator, field_serializer

import src.components.config as config
from src.components.utils import render_template_str

database_name = config.CONFIG_PROJECT_NAME
global_collection_name = config.CONFIG_GLOBAL_COLLECTION_NAME
user_collection_name = config.CONFIG_USER_COLLECTION_NAME
pod_collection_name = config.CONFIG_POD_COLLECTION_NAME
template_collection_name = config.CONFIG_TEMPLATE_COLLECTION_NAME


class GlobalModel(BaseModel):
    """
    Global model, used to store global settings in the database
    """
    uid_counter: int = 0
    flag_crashed: bool = False  # record if last run crashed
    version: str = config.CONFIG_BUILD_VERSION


class UserRoleEnum(str, Enum):
    """
    User role enum, used to define user roles
    """
    super_admin = "super_admin"
    admin = "admin"
    user = "user"


class FieldTypeEnum(str, Enum):
    """
    Field type enum, used to define field types
    """
    string = "str"
    integer = "int"
    float = "float"
    boolean = "bool"
    datetime = "datetime"
    list = "list"


class ResourceStatusEnum(str, Enum):
    """
    Resource status enum, used to define resource status. (for error recovery)
    """
    committed = "committed"
    deleted = "deleted"
    pending = "pending"


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


class UserStatusEnum(str, Enum):
    """
    User status enum, used to define user status.
    """
    active = "active"
    inactive = "inactive"


class QuotaModel(BaseModel):
    """
    Quota model, used to define user quota
    """
    version: str
    committed: bool = False
    cpu_m: int
    memory_mb: int
    storage_mb: int
    gpu: int  # attention: not used
    network_mb: int  # attention: not used
    pod_n: int

    @field_validator("version")
    def version_must_be_valid(cls, v):
        if v is None or v == "":
            v = config.CONFIG_BUILD_VERSION
        return v

    @classmethod
    def new(cls,
            cpu_m: int,
            memory_mb: int,
            storage_mb: int,
            pod_n: int,
            gpu: int = 0,
            network_mb: int = 0,
            ):
        return cls(
            version=config.CONFIG_BUILD_VERSION,
            cpu_m=cpu_m,
            memory_mb=memory_mb,
            storage_mb=storage_mb,
            gpu=gpu,
            network_mb=network_mb,
            pod_n=pod_n,
        )

    @classmethod
    def default_quota(cls):
        return cls(
            version=config.CONFIG_BUILD_VERSION,
            cpu_m=8000,
            memory_mb=16384,
            storage_mb=51200,
            gpu=0,
            network_mb=0,
            pod_n=10,
        )

    def update_from_dict(self, d: Dict[str, Any]) -> Self:
        if d is None:
            return self
        for k, v in d.items():
            if hasattr(self, k) and v is not None and k not in ['version', 'committed']:
                setattr(self, k, v)
        self.model_validate(self)
        return self

    @classmethod
    def upgrade(cls, d: Dict[str, Any]) -> Self:
        res = cls(**d)
        res.version = config.CONFIG_BUILD_VERSION
        return res


class UserModel(BaseModel):
    """
    User model, used to define user
    """
    version: str
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    uid: int
    uuid: Optional[UUID4]
    username: str
    status: UserStatusEnum = UserStatusEnum.active
    email: Optional[EmailStr]
    password: SecretStr
    htpasswd: Optional[SecretStr] = None  # used for htpasswd authentication
    role: UserRoleEnum
    owned_pod_ids: List[UUID4]  # not used
    quota: Optional[QuotaModel]
    extra_info: Optional[Dict[str, Any]] = None

    @field_validator("version")
    def version_must_be_valid(cls, v):
        if v is None or v == "":
            v = config.CONFIG_BUILD_VERSION
        return v

    @field_validator("uuid")
    def uuid_must_be_valid(cls, v):
        if v is None:
            v = uuid.uuid4()
        if not isinstance(v, uuid.UUID):
            v = uuid.UUID(v)
        return v

    @field_serializer('uuid')
    def serialize_uuid(self, v: uuid.UUID, _info):
        return str(v)

    @field_serializer('password')
    def serialize_password(self, v: SecretStr, _info):
        return v.get_secret_value()

    @field_serializer('htpasswd')
    def serialize_htpasswd(self, v: SecretStr, _info):
        if v is None:
            return None
        else:
            return v.get_secret_value()

    @field_serializer('role')
    def serialize_role(self, v: UserRoleEnum, _info):
        return v.value

    @field_serializer('status')
    def serialize_status(self, v: UserStatusEnum, _info):
        return v.value

    @field_validator("owned_pod_ids")
    def owned_pod_ids_must_be_valid(cls, v):
        if v is None:
            v = []
        return v

    @field_validator("quota")
    def quota_must_be_valid(cls, v):
        if isinstance(v, dict):
            v = QuotaModel(**v)
        return v

    @classmethod
    def new(cls,
            uid: int,
            username: str,
            password: str,
            role: UserRoleEnum,
            email: Optional[str] = None,
            quota: Optional[Dict[str, Any]] = None,
            extra_info: Optional[Dict[str, Any]] = None):
        return cls(
            version=config.CONFIG_BUILD_VERSION,
            uid=uid,
            uuid=None,
            username=username,
            email=email,
            password=sha256(password.encode()).hexdigest(),
            htpasswd=f"{username}:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode(),
            role=role,
            owned_pod_ids=[],
            quota=quota,
            extra_info=extra_info,
        )

    @classmethod
    def upgrade(cls, d: Dict[str, Any]) -> Self:
        version = d['version']
        # if version <= "v0.0.3":
        #     return cls(
        #         version=config.CONFIG_BUILD_VERSION,
        #         uid=d['uid'],
        #         uuid=d['uuid'],
        #         username=d['username'],
        #         email=d['email'],
        #         password=d['password'],
        #         htpasswd=d['htpasswd'],
        #         role=d['role'],
        #         owned_pod_ids=d['owned_pod_ids'],
        #         quota=QuotaModel(**d['quota']),
        #     )
        # else:
        res = cls(**d)
        res.version = config.CONFIG_BUILD_VERSION
        return res


class TemplateModel(BaseModel):
    """
    Template model, used to define template
    """
    version: str
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    template_id: UUID4
    name: str
    description: str
    image_ref: str
    template_str: str
    fields: Optional[Dict[str, FieldTypeEnum]]  # not used
    defaults: Optional[Dict[str, Any]]  # not used

    @field_validator("version")
    def version_must_be_valid(cls, v):
        if v is None or v == "":
            v = config.CONFIG_BUILD_VERSION
        return v

    @field_validator("template_id")
    def uuid_must_be_valid(cls, v):
        if v is None:
            v = uuid.uuid4()
        if not isinstance(v, uuid.UUID):
            v = uuid.UUID(v)
        return v

    @field_serializer('template_id')
    def serialize_uuid(self, v: uuid.UUID, _info):
        return str(v)

    @field_serializer('fields')
    def serialize_fields(self, v: Dict[str, FieldTypeEnum], _info):
        if v is not None:
            return {
                _k: str(_v) for _k, _v in v.items()
            }
        else:
            return None

    @classmethod
    def new(cls,
            name: str,
            description: str,
            image_ref: str,
            template_str: str,
            fields: Optional[Dict[str, Any]],
            defaults: Optional[Dict[str, Any]]):
        return cls(
            version=config.CONFIG_BUILD_VERSION,
            template_id=uuid.uuid4(),
            name=name,
            description=description,
            image_ref=image_ref,
            template_str=template_str,
            fields=fields,
            defaults=defaults,
        )

    # example values to test if template is valid
    # attention: strong dependency on project design
    __EXAMPLE_VALUES__ = {
        "POD_LABEL": config.CONFIG_K8S_POD_LABEL_FMT.format("test_id"),
        "POD_ID": "test_id",
        "POD_IMAGE_REF": "davidliyutong/code-server-speit:latest",
        "POD_CPU_LIM": "2000m",
        "POD_MEM_LIM": "4096Mi",
        "POD_STORAGE_LIM": "10Mi",
        "POD_REPLICAS": "1",
        "POD_AUTH": config.CONFIG_K8S_CREDENTIAL_FMT.format("username"),
        "CONFIG_CODER_HOSTNAME": "code.example.org",
        "CONFIG_CODER_TLS_SECRET": "code-tls-secret",
        "CONFIG_VNC_HOSTNAME": "vnc.example.org",
        "CONFIG_VNC_TLS_SECRET": "vnc-tls-secret",
    }

    def verify(self) -> bool:
        template_str, used_keys, _ = render_template_str(self.template_str, self.__EXAMPLE_VALUES__)
        return len(set(used_keys)) == len(self.__EXAMPLE_VALUES__)

    @property
    def values(self):
        return {
            'POD_IMAGE_REF': self.image_ref,
        }

    @classmethod
    def upgrade(cls, d: Dict[str, Any]) -> Self:
        res = cls(**d)
        res.version = config.CONFIG_BUILD_VERSION
        return res


class PodModel(BaseModel):
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
            v = config.CONFIG_BUILD_VERSION
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
            "POD_LABEL": config.CONFIG_K8S_POD_LABEL_FMT.format(self.pod_id),
            "POD_ID": self.pod_id,
            "POD_CPU_LIM": str(self.cpu_lim_m_cpu) + "m",
            "POD_MEM_LIM": str(self.mem_lim_mb) + "Mi",
            "POD_STORAGE_LIM": str(self.storage_lim_mb) + "Mi",
            "POD_AUTH": config.CONFIG_K8S_CREDENTIAL_FMT.format(str(self.user_uuid)),
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
            version=config.CONFIG_BUILD_VERSION,
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
        res.version = config.CONFIG_BUILD_VERSION
        return res


from sanic_ext import openapi

# attention: registrate components
openapi.component(PodModel)
openapi.component(UserRoleEnum)
openapi.component(FieldTypeEnum)
openapi.component(ResourceStatusEnum)
openapi.component(PodStatusEnum)
openapi.component(PodStatusEnum)
openapi.component(UserStatusEnum)
openapi.component(QuotaModel)
openapi.component(UserModel)
openapi.component(TemplateModel)
openapi.component(PodModel)
