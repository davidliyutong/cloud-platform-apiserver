import datetime
import uuid
from hashlib import sha256
import bcrypt
import shortuuid

from pydantic import BaseModel, UUID4, EmailStr, SecretStr
from pydantic import field_validator, field_serializer
from typing import List, Optional, Dict, Any, Union

from enum import Enum

from src.components.utils import render_template_str
import src.components.config as config

database_name = config.CONFIG_PROJECT_NAME
global_collection_name = config.CONFIG_GLOBAL_COLLECTION_NAME
user_collection_name = config.CONFIG_USER_COLLECTION_NAME
pod_collection_name = config.CONFIG_POD_COLLECTION_NAME
template_collection_name = config.CONFIG_TEMPLATE_COLLECTION_NAME


class GlobalModel(BaseModel):
    uid_counter: int = 0


class RoleEnum(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    user = "user"


class FieldTypeEnum(str, Enum):
    string = "str"
    integer = "int"
    float = "float"
    boolean = "bool"
    datetime = "datetime"
    list = "list"


class ResourceStatusEnum(str, Enum):
    committed = "committed"
    deleted = "deleted"
    pending = "pending"


class PodStatusEnum(str, Enum):
    pending = "pending"  # current
    creating = "creating"  # current (unused)
    running = "running"  # current | target
    stopped = "stopped"  # current | target
    deleting = "deleting"  # current (unused)
    failed = "failed"  # current
    unknown = "unknown"  # current


class UserStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"


class QuotaModel(BaseModel):
    committed: bool = False
    m_cpu: int
    memory_mb: int
    storage_mb: int
    gpu: int
    network_mb: int
    pod: int


class UserModel(BaseModel):
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    uid: int
    uuid: Optional[UUID4]
    username: str
    status: UserStatusEnum = UserStatusEnum.active
    email: Optional[EmailStr]
    password: SecretStr
    htpasswd: Optional[SecretStr] = None
    role: RoleEnum
    owned_pod_ids: List[UUID4]
    quota: Optional[QuotaModel]

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
    def serialize_role(self, v: RoleEnum, _info):
        return v.value

    @field_serializer('status')
    def serialize_status(self, v: UserStatusEnum, _info):
        return v.value

    @field_validator("owned_pod_ids")
    def owned_pod_ids_must_be_valid(cls, v):
        if v is None:
            v = []
        return v

    @classmethod
    def new(cls,
            uid: int,
            username: str,
            password: str,
            role: RoleEnum,
            email: Optional[str] = None,
            quota: Optional[Dict[str, Any]] = None):
        return cls(
            uid=uid,
            uuid=None,
            username=username,
            email=email,
            password=sha256(password.encode()).hexdigest(),
            htpasswd=f"{username}:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode(),
            role=role,
            owned_pod_ids=[],
            quota=quota,
        )


class TemplateModel(BaseModel):
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    template_id: UUID4
    name: str
    description: str
    image_ref: str
    template_str: str
    fields: Optional[Dict[str, FieldTypeEnum]]
    defaults: Optional[Dict[str, Any]]

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
            template_id=uuid.uuid4(),
            name=name,
            description=description,
            image_ref=image_ref,
            template_str=template_str,
            fields=fields,
            defaults=defaults,
        )

    __EXAMPLE_VALUES__ = {
        "POD_LABEL": config.CONFIG_K8S_POD_LABEL_FMT.format("test_id"),
        "POD_ID": "test_id",
        "POD_IMAGE_REF": "davidliyutong/code-server-speit:latest",
        "POD_CPU_LIM": "2000m",
        "POD_MEM_LIM": "4096Mi",
        "POD_STORAGE_LIM": "10Mi",
        "POD_REPLICAS": "1",
        "POD_AUTH": config.CONFIG_K8S_CREDENTIAL_FMT.format("username"),
        "CONFIG_CODE_HOSTNAME": "code.example.org",
        "CONFIG_CODE_TLS_SECRET": "code-tls-secret",
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


class PodModel(BaseModel):
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    pod_id: str
    name: str
    description: str
    template_ref: UUID4
    cpu_lim_m_cpu: int
    mem_lim_mb: int
    storage_lim_mb: int
    username: str
    created_at: datetime.datetime
    started_at: datetime.datetime
    timeout_s: int
    current_status: PodStatusEnum
    target_status: PodStatusEnum

    @field_serializer('template_ref')
    def serialize_uuid(self, v: uuid.UUID, _info):
        return str(v)

    @field_validator('created_at')
    def validate_created_at(cls, v: Union[str, datetime.datetime]):
        if isinstance(v, str):
            v = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
        return v

    @field_serializer('created_at')
    def serialize_created_at(self, v: datetime.datetime, _info):
        return v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @field_serializer('started_at')
    def serialize_started_at(self, v: datetime.datetime, _info):
        return v.timestamp()

    @property
    def values(self):
        return {
            "POD_LABEL": config.CONFIG_K8S_POD_LABEL_FMT.format(self.pod_id),
            "POD_ID": self.pod_id,
            "POD_CPU_LIM": str(self.cpu_lim_m_cpu) + "m",
            "POD_MEM_LIM": str(self.mem_lim_mb) + "Mi",
            "POD_STORAGE_LIM": str(self.storage_lim_mb) + "Mi",
            "POD_AUTH": config.CONFIG_K8S_CREDENTIAL_FMT.format(self.username),
            "POD_REPLICAS": "1" if self.target_status == PodStatusEnum.running else "0",
        }

    @classmethod
    def new(cls,
            template_ref: Optional[str],
            username: str,
            name: str = "",
            description: str = "",
            cpu_lim_m_cpu: int = 1000,
            mem_lim_mb: int = 512,
            storage_lim_mb: int = 10240,
            timeout_s: int = 3600):
        return cls(
            pod_id=shortuuid.uuid(),
            name=name,
            description=description,
            template_ref=uuid.UUID(template_ref),
            cpu_lim_m_cpu=cpu_lim_m_cpu,
            mem_lim_mb=mem_lim_mb,
            storage_lim_mb=storage_lim_mb,
            username=username,
            created_at=datetime.datetime.now(),
            started_at=datetime.datetime.fromtimestamp(0),
            timeout_s=timeout_s,
            current_status=PodStatusEnum.pending,
            target_status=PodStatusEnum.running,
        )
