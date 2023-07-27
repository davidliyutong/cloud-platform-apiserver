import datetime
from typing import List, Optional, Dict, Any

import src.components.datamodels as datamodels

from pydantic import BaseModel, field_serializer, EmailStr, SecretStr


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
    uid: int
    timeout_s: int
    values: Optional[Dict[str, Any]] = None


class PodCreateResponse(ResponseBaseModel):
    pod: datamodels.PodModel = None


class PodGetRequest(BaseModel):
    pod_id: str


class PodGetResponse(PodCreateResponse):
    pass


class PodUpdateRequest(BaseModel):
    pod_id: str
    name: str = None
    description: str = None
    template_ref: str = None
    uid: int = None
    timeout_s: int = None
    target_status: str = None


class PodUpdateResponse(TemplateGetResponse):
    pass


class PodDeleteRequest(PodGetRequest):
    pass


class PodDeleteResponse(TemplateGetResponse):
    pass
