import datetime
import uuid
from hashlib import sha256
import bcrypt
import shortuuid

from pydantic import BaseModel, UUID4, EmailStr, SecretStr, SecretBytes
from pydantic import field_validator, field_serializer
from typing import List, Optional, Dict, Any

from enum import Enum

from src.components.utils import parse_template_str
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
    pending = "pending"
    creating = "creating"
    running = "running"
    stopped = "stopped"
    deleting = "deleting"
    failed = "failed"
    unknown = "unknown"


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
    template_name: str
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
            template_name: str,
            description: str,
            image_ref: str,
            template_str: str,
            fields: Optional[Dict[str, Any]],
            defaults: Optional[Dict[str, Any]]):
        return cls(
            template_id=uuid.uuid4(),
            template_name=template_name,
            description=description,
            image_ref=image_ref,
            template_str=template_str,
            fields=fields,
            defaults=defaults,
        )

    __EXAMPLE_VALUES__ = {
        "POD_ID": "test_id",
        "POD_IMAGE_REF": "davidliyutong/code-server-speit:latest",
        "POD_CPU_LIM": "2000m",
        "POD_MEM_LIM": "4096Mi",
        "POD_STORAGE_LIM": "10Mi",
        "POD_AUTH": "uid-basic-auth",
        "CONFIG_CODE_HOSTNAME": "code.example.org",
        "CONFIG_CODE_TLS_SECRET": "code-tls-secret",
        "CONFIG_VNC_HOSTNAME": "vnc.example.org",
        "CONFIG_VNC_TLS_SECRET": "vnc-tls-secret",
    }

    def verify(self) -> bool:
        template_str, used_keys, _ = parse_template_str(self.template_str, self.__EXAMPLE_VALUES__)
        return len(set(used_keys)) == len(self.__EXAMPLE_VALUES__)


class PodModel(BaseModel):
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    pod_id: str
    name: str
    description: str
    image_ref: str
    template_ref: UUID4
    cpu_lim_m_cpu: int
    mem_lim_mb: int
    storage_lim_mb: int
    uid: int
    created_at: datetime.datetime
    started_at: datetime.datetime
    timeout_s: int
    current_status: PodStatusEnum
    target_status: PodStatusEnum

    def render(self):
        return {
            "POD_ID": self.pod_id,
            "POD_IMAGE_REF": self.image_ref,
            "POD_CPU_LIM": str(self.cpu_lim_m_cpu) + "m",
            "POD_MEM_LIM": str(self.mem_lim_mb) + "Mi",
            "POD_STORAGE_LIM": str(self.storage_lim_mb) + "Mi",
            "POD_AUTH": f"{self.uid}-basic-auth",
        }

    @classmethod
    def new(cls,
            image_ref: str,
            template_ref: UUID4,
            uid: int,
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
            image_ref=image_ref,
            template_ref=template_ref,
            cpu_lim_m_cpu=cpu_lim_m_cpu,
            mem_lim_mb=mem_lim_mb,
            storage_lim_mb=storage_lim_mb,
            uid=uid,
            created_at=datetime.datetime.now(),
            started_at=datetime.datetime.now(),
            timeout_s=timeout_s,
            current_status=PodStatusEnum.pending.value,
            target_status=PodStatusEnum.running,
        )
