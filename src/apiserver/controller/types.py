"""
This file defines the types of the request and response of the apiserver.
"""
import uuid
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, EmailStr, field_validator

import src.components.datamodels as datamodels


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
    users: List[datamodels.UserModel] = []


class UserCreateRequest(BaseModel):
    """
    Create request for users
    """
    username: str
    password: str
    email: Optional[str]
    role: str  # see datamodels.RoleEnum
    quota: Optional[Dict[str, Any]] = None  # resource quota


class UserCreateResponse(ResponseBaseModel):
    """
    Create response for users
    """
    user: datamodels.UserModel = None


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
    password: Optional[str] = None
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    quota: Optional[Dict[str, Any]] = None

    @field_validator('username')
    def username_must_be_valid(cls, v):
        if v == "" or v is None:
            raise ValueError("username cannot be empty")
        return v

    @field_validator('password')
    def password_must_be_valid(cls, v):
        if v == "" or v is None:
            raise ValueError("password cannot be empty")
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
    templates: List[datamodels.TemplateModel] = []


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
    template: datamodels.TemplateModel = None


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
    name: str = None
    description: str = None
    image_ref: str = None
    template_str: str = None
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
    pods: List[datamodels.PodModel] = []


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
        if v == "" or v is None:
            raise ValueError("template_ref cannot be empty")
        try:
            _ = uuid.UUID(v)
        except ValueError as e:
            raise e
        return v

    @field_validator('cpu_lim_m_cpu')
    def cpu_lim_m_cpu_must_be_valid(cls, v):
        if v < 0:
            raise ValueError('cpu_lim_m_cpu must be positive')
        if v < 500:
            raise ValueError('cpu_lim_m_cpu must be greater than 500 mCPU')
        return v

    @field_validator('mem_lim_mb')
    def mem_lim_mb_must_be_valid(cls, v):
        if v < 0:
            raise ValueError('mem_lim_mb must be positive')
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
    pod: datamodels.PodModel = None


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
    username: Optional[str] = None
    timeout_s: Optional[int] = None
    target_status: Optional[datamodels.PodStatusEnum] = None

    @field_validator('timeout_s')
    def timeout_s_must_be_valid(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('timeout_s must be positive')
            elif v > 86400:
                raise ValueError('timeout_s must be less than 86400 seconds')
        return v

    @field_validator('target_status')
    def target_status_must_be_valid(cls, v):
        if isinstance(v, str):
            v = datamodels.PodStatusEnum(v)
        if v is not None and v not in datamodels.PodStatusEnum:
            raise ValueError('target_status must be valid PodStatusEnum')

        if v not in [datamodels.PodStatusEnum.running, datamodels.PodStatusEnum.stopped]:
            raise ValueError('target_status must be valid')
        return v


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
