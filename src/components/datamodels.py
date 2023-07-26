import datetime
import uuid
from hashlib import sha256

from pydantic import BaseModel, UUID4, EmailStr, SecretStr, SecretBytes
from pydantic import field_validator, field_serializer
from typing import List, Optional, Dict, Any

from enum import Enum

database_name = "clpl"
global_collection_name = "clpl_global"
user_collection_name = "clpl_users"
pod_collection_name = "clpl_pods"
template_collection_name = "clpl_templates"


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
    m_cpu: int
    memory_mb: int
    storage_mb: int
    gpu: int
    network_mb: int
    pod: int


class UserModel(BaseModel):
    uid: int
    uuid: Optional[UUID4]
    username: str
    status: UserStatusEnum = UserStatusEnum.active
    email: Optional[EmailStr]
    password: SecretStr
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


def new_user_model(uid: int,
                   username: str,
                   password: str,
                   role: RoleEnum,
                   email: Optional[str] = None,
                   quota: Optional[Dict[str, Any]] = None) -> UserModel:
    return UserModel(
        uid=uid,
        uuid=None,
        username=username,
        email=email,
        password=sha256(password.encode()).hexdigest(),
        role=role,
        owned_pod_ids=[],
        quota=quota,
    )


class TemplateModel(BaseModel):
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
        return {
            _k: str(_v) for _k, _v in v.items()
        }


class PodModel(BaseModel):
    pod_id: UUID4
    name: str
    description: str
    template_ref: UUID4
    uid: int
    created_at: datetime.datetime
    started_at: datetime.datetime
    timeout_s: int
    current_status: str
    target_status: str
