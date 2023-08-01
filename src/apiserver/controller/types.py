from typing import List, Optional, Dict, Any

from pydantic import BaseModel, EmailStr, field_validator

import src.components.datamodels as datamodels


class ListRequestBaseModel(BaseModel):
    index_start: int = -1
    index_end: int = -1
    extra_query_filter: str = ''


class ResponseBaseModel(BaseModel):
    description: str = ""
    status: int
    message: str


class UserListRequest(ListRequestBaseModel):
    pass


class UserListResponse(ResponseBaseModel):
    total_users: int = 0
    users: List[datamodels.UserModel] = []


class UserCreateRequest(BaseModel):
    username: str
    password: str
    email: Optional[str]
    role: str
    quota: Optional[Dict[str, Any]] = None


class UserCreateResponse(ResponseBaseModel):
    user: datamodels.UserModel = None


class UserGetRequest(BaseModel):
    username: str


class UserGetResponse(UserCreateResponse):
    pass


class UserUpdateRequest(BaseModel):
    username: str
    password: Optional[str] = None
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    quota: Optional[Dict[str, Any]] = None


class UserUpdateResponse(UserGetResponse):
    pass


class UserDeleteRequest(UserGetRequest):
    pass


class UserDeleteResponse(UserGetResponse):
    pass


class TemplateListRequest(ListRequestBaseModel):
    pass


class TemplateListResponse(ResponseBaseModel):
    total_templates: int = 0
    templates: List[datamodels.TemplateModel] = []


class TemplateCreateRequest(BaseModel):
    template_name: str
    description: str
    image_ref: str
    template_str: str
    fields: Optional[Dict[str, Any]]
    defaults: Optional[Dict[str, Any]]
    pass


class TemplateCreateResponse(ResponseBaseModel):
    template: datamodels.TemplateModel = None


class TemplateGetRequest(BaseModel):
    template_id: str


class TemplateGetResponse(TemplateCreateResponse):
    pass


class TemplateUpdateRequest(BaseModel):
    template_id: str
    template_name: str = None
    description: str = None
    image_ref: str = None
    template_str: str = None
    fields: Optional[Dict[str, Any]] = None
    defaults: Optional[Dict[str, Any]] = None


class TemplateUpdateResponse(TemplateGetResponse):
    pass


class TemplateDeleteRequest(TemplateGetRequest):
    pass


class TemplateDeleteResponse(TemplateGetResponse):
    pass


class PodListRequest(ListRequestBaseModel):
    pass


class PodListResponse(ResponseBaseModel):
    total_pods: int = 0
    pods: List[datamodels.PodModel] = []


class PodCreateRequest(BaseModel):
    name: str
    description: str
    template_ref: str
    cpu_lim_m_cpu: int
    mem_lim_mb: int
    storage_lim_mb: int
    username: str
    timeout_s: Optional[int] = None
    values: Optional[Dict[str, Any]] = None

    @field_validator('cpu_lim_m_cpu')
    def cpu_lim_m_cpu_must_be_valid(cls, v):
        if v < 0:
            raise ValueError('cpu_lim_m_cpu must be positive')
        return v

    @field_validator('mem_lim_mb')
    def mem_lim_mb_must_be_valid(cls, v):
        if v < 0:
            raise ValueError('mem_lim_mb must be positive')
        return v

    @field_validator('storage_lim_mb')
    def storage_lim_mb_must_be_valid(cls, v):
        if v < 0:
            raise ValueError('storage_lim_mb must be positive')
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
    pod: datamodels.PodModel = None


class PodGetRequest(BaseModel):
    pod_id: str


class PodGetResponse(PodCreateResponse):
    pass


class PodUpdateRequest(BaseModel):
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

    @field_validator('target_status')
    def target_status_must_be_valid(cls, v):
        if v is not None and v not in datamodels.PodStatusEnum:
            raise ValueError('target_status must be valid PodStatusEnum')
        return v


class PodUpdateResponse(PodGetResponse):
    pass


class PodDeleteRequest(PodGetRequest):
    pass


class PodDeleteResponse(PodGetResponse):
    pass
