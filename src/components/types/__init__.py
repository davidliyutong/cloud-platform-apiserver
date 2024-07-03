"""
This file defines the types of the request and response of the apiserver.
"""
import uuid
from typing import List, Optional, Dict, Any, Tuple, Union

from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field, field_serializer, SecretStr

from src.components.datamodels import (
    TemplateModel,
    PodModelV1,
    PodStatusEnum,
    RBACPolicyModelV2,
    UserStatusEnum,
    QuotaModelV2,
    UserModelV2
)
from src.components.datamodels.group import GroupEnumInternal


def _ensure_uuid_value(v):
    if v == "" or v is None:
        raise ValueError("uuid cannot be empty")
    try:
        _ = uuid.UUID(v)
    except ValueError as e:
        raise e
    return v


def _ensure_non_empty_value(v, field_name=""):
    if v == "":
        raise ValueError(f"field[{field_name}] cannot be empty")
    return v


class ListRequestBaseModel(BaseModel):
    """
    Base model for list request
    """
    index_start: int = -1  # -1 means start from the beginning
    index_end: int = -1  # -1 means end at the end
    extra_query_filter: str = ''  # mongodb query filter in json format


class ResponseBaseModel(BaseModel):
    """
    Base model for response
    """
    description: str = ""  # description of the response
    status: int  # status code of the response
    message: str  # message of the response


class UserListRequest(ListRequestBaseModel):
    """
    List request for users
    """
    pass


class UserListResponse(ResponseBaseModel):
    """
    List response for users
    """
    total_users: int = 0
    users: List[UserModelV2] = []

    @field_serializer('users')
    def serialize_users(self, v: List[UserModelV2], _info):
        for user in v:
            user.password = SecretStr("******")
            user.otp_secret = SecretStr("******")
        return v


class UserCreateRequest(BaseModel):
    """
    Create request for users
    """
    username: str
    group: Optional[str] = GroupEnumInternal.default
    password: str
    email: Optional[str] = None
    quota: Optional[Dict[str, Any]] = None  # resource quota
    extra_info: Optional[Dict[str, Any]] = None  # extra info


class UserCreateResponse(ResponseBaseModel):
    """
    Create response for users
    """
    user: Optional[UserModelV2] = None

    @field_serializer('user')
    def serialize_user(self, v: UserModelV2, _info):
        if v is not None:
            v.password = SecretStr("******")
            v.otp_secret = SecretStr("******")
        return v


class UserGetRequest(BaseModel):
    """
    Get request for users
    """
    username: str


class UserGetResponse(UserCreateResponse):
    """
    Get response for users, the same as create response
    """
    pass


class UserUpdateRequest(BaseModel):
    """
    Update request for users, all fields except username are optional.
    None means no change.
    """
    username: str
    email: Optional[EmailStr] = None
    extra_info: Optional[Dict[str, Any]] = None
    public_keys: Optional[List[str]] = None

    update_password: bool = False
    new_password: Optional[str] = None
    old_password: Optional[str] = None

    update_quota: bool = False
    quota: Optional[QuotaModelV2] = None

    update_group: bool = False
    group: Optional[str] = None

    update_status: bool = False
    status: Optional[UserStatusEnum] = None

    update_otp: bool = False
    otp_secret: Optional[str] = None

    update_otp_status: bool = False
    otp_code: Optional[str] = None
    otp_enabled: Optional[bool] = None

    @field_validator('username')
    def username_must_be_valid(cls, v):
        return _ensure_non_empty_value(v, "username")

    @field_validator('new_password')
    def new_password_must_be_valid(cls, v):
        if v is not None:
            return _ensure_non_empty_value(v, "new_password")
        return v


class UserUpdateResponse(UserGetResponse):
    """
    Update response for users, the same as get response
    """
    pass


class UserDeleteRequest(UserGetRequest):
    """
    Delete request for users, the same as get request
    """
    otp_code: Optional[str] = None
    password: Optional[str] = None
    pass


class UserDeleteResponse(UserGetResponse):
    """
    Delete response for users, the same as get response
    """
    pass


class TemplateListRequest(ListRequestBaseModel):
    """
    List request for templates
    """
    pass


class TemplateListResponse(ResponseBaseModel):
    """
    List response for templates
    """
    total_templates: int = 0
    templates: List[TemplateModel] = []


class TemplateCreateRequest(BaseModel):
    """
    Create request for templates.
    fields and defaults are optional and not yet used.
    """
    name: str
    description: str
    image_ref: str
    template_str: str
    fields: Optional[Dict[str, Any]]
    defaults: Optional[Dict[str, Any]]
    pass


class TemplateCreateResponse(ResponseBaseModel):
    """
    Create response for templates
    """
    template: TemplateModel = None


class TemplateGetRequest(BaseModel):
    """
    Get request for templates
    """
    template_id: str


class TemplateGetResponse(TemplateCreateResponse):
    """
    Get response for templates, the same as create response
    """
    pass


class TemplateUpdateRequest(BaseModel):
    """
    Update request for templates, all fields except template_id are optional.
    """
    template_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    image_ref: Optional[str] = None
    template_str: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    defaults: Optional[Dict[str, Any]] = None


class TemplateUpdateResponse(TemplateGetResponse):
    """
    Update response for templates, the same as get response
    """
    pass


class TemplateDeleteRequest(TemplateGetRequest):
    """
    Delete request for templates, the same as get request
    """
    pass


class TemplateDeleteResponse(TemplateGetResponse):
    """
    Delete response for templates, the same as get response
    """
    pass


class PodListRequest(ListRequestBaseModel):
    """
    List request for pods
    """
    pass


class PodListResponse(ResponseBaseModel):
    """
    List response for pods
    """
    total_pods: int = 0
    pods: List[PodModelV1] = []


class PodCreateRequest(BaseModel):
    """
    Create request for pods. values is the values for the template (not used).
    timeout_s is the timeout for the pod to run. max is 86400 seconds (24 hours).
    """
    name: str
    description: str
    template_ref: str
    cpu_lim_m_cpu: int
    mem_lim_mb: int
    storage_lim_mb: int
    username: Optional[str] = None
    timeout_s: Optional[int] = None
    values: Optional[Dict[str, Any]] = None

    @field_validator('template_ref')
    def template_ref_must_be_valid(cls, v):
        return _ensure_uuid_value(v)

    @field_validator('cpu_lim_m_cpu')
    def cpu_lim_m_cpu_must_be_valid(cls, v):
        if v < 500:
            raise ValueError('cpu_lim_m_cpu must be greater than 500 mCPU')
        return v

    @field_validator('mem_lim_mb')
    def mem_lim_mb_must_be_valid(cls, v):
        if v < 512:
            raise ValueError('mem_lim_mb must be greater than 512 MB')
        return v

    @field_validator('storage_lim_mb')
    def storage_lim_mb_must_be_valid(cls, v):
        if v < 10240:
            raise ValueError('storage_lim_mb must be greater than 10240 MB')
        return v

    @field_validator('timeout_s')
    def timeout_s_must_be_valid(cls, v):
        if v is None:
            v = 3600
        if v < 0:
            raise ValueError('timeout_s must be positive')
        elif v > 86400:
            raise ValueError('timeout_s must be less than 86400 seconds')
        return v


class PodCreateResponse(ResponseBaseModel):
    """
    Create response for pods
    """
    pod: PodModelV1 = None


class PodGetRequest(BaseModel):
    """
    Get request for pods
    """
    pod_id: str


class PodGetResponse(PodCreateResponse):
    """
    Get response for pods, the same as create response
    """
    pass


class PodUpdateRequest(BaseModel):
    """
    Update request for pods, all fields except pod_id are optional.
    target_status is the target status for the pod to reach. Can be either running or stopped.
    """
    pod_id: Optional[str]
    name: Optional[str] = None
    description: Optional[str] = None
    cpu_lim_m_cpu: Optional[int] = None
    mem_lim_mb: Optional[int] = None
    storage_lim_mb: Optional[int] = None
    username: Optional[str] = None
    user_uuid: Optional[str] = None
    timeout_s: Optional[int] = None
    target_status: Optional[PodStatusEnum] = None
    force: bool = False

    @model_validator(mode="after")
    def validate_request(self):
        if self.timeout_s is not None:
            if self.timeout_s < 0:
                raise ValueError('timeout_s must be positive')
            elif self.timeout_s > 86400 and not self.force:
                raise ValueError('timeout_s must be less than 86400 seconds')

    @field_validator('target_status')
    def target_status_must_be_valid(cls, v):
        if isinstance(v, str):
            v = PodStatusEnum(v)
        if v is not None and v not in PodStatusEnum:
            raise ValueError('target_status must be valid PodStatusEnum')

        if v not in [PodStatusEnum.running, PodStatusEnum.stopped]:
            raise ValueError('target_status must be valid')
        return v

    @field_validator('cpu_lim_m_cpu')
    def cpu_lim_m_cpu_must_be_valid(cls, v):
        return PodCreateRequest.cpu_lim_m_cpu_must_be_valid(v) if v is not None else v

    @field_validator('mem_lim_mb')
    def mem_lim_mb_must_be_valid(cls, v):
        return PodCreateRequest.mem_lim_mb_must_be_valid(v) if v is not None else v

    @field_validator('storage_lim_mb')
    def storage_lim_mb_must_be_valid(cls, v):
        return PodCreateRequest.storage_lim_mb_must_be_valid(v) if v is not None else v


class PodUpdateResponse(PodGetResponse):
    """
    Update response for pods, the same as get response
    """
    pass


class PodDeleteRequest(PodGetRequest):
    """
    Delete request for pods, the same as get request
    """
    pass


class PodDeleteResponse(PodGetResponse):
    """
    Delete response for pods, the same as get response
    """
    pass


class OIDCStatusResponse(BaseModel):
    name: str
    path: str


class PolicyListRequest(ListRequestBaseModel):
    pass


class PolicyListResponse(ResponseBaseModel):
    policies: List[RBACPolicyModelV2] = []


class PolicyCreateRequest(BaseModel):
    subject_uuid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    policies: List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]] = Field(default_factory=list)

    @field_validator('subject_uuid')
    def subject_uuid_must_be_valid(cls, v):
        return _ensure_uuid_value(v if v is not None else str(uuid.uuid4()))


class PolicyCreateResponse(ResponseBaseModel):
    policy: RBACPolicyModelV2 = None


class PolicyGetRequest(BaseModel):
    subject_uuid: str = ""


class PolicyGetResponse(ResponseBaseModel):
    policy: RBACPolicyModelV2 = None


class PolicyUpdateRequest(BaseModel):
    subject_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    policies: Optional[List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]]] = None


class PolicyUpdateResponse(ResponseBaseModel):
    pass


class PolicyDeleteRequest(BaseModel):
    subject_uuid: str = ""

    @field_validator('subject_uuid')
    def subject_uuid_must_be_valid(cls, v):
        return _ensure_uuid_value(v)


class PolicyDeleteResponse(ResponseBaseModel):
    pass


class EnforceRequest(BaseModel):
    subject: str = ""
    object: str = ""
    action: str = ""


class EnforceResponse(ResponseBaseModel):
    result: bool = False
