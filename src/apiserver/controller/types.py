import datetime
from typing import List, Optional, Dict, Any

import src.components.datamodels as datamodels

from pydantic import BaseModel, field_serializer, EmailStr, SecretStr


class AdminUserListRequest(BaseModel):
    index_start: int = -1
    index_end: int = -1
    extra_query_filter: str = ''


class AdminUserListResponse(BaseModel):
    description: str = ""
    status: int
    message: str
    total_users: int = 0
    users: List[datamodels.UserModel] = []


class AdminUserCreateRequest(BaseModel):
    username: str
    password: str
    email: Optional[str]
    role: str
    quota: Optional[Dict[str, Any]] = None


class AdminUserCreateResponse(BaseModel):
    description: str = ""
    status: int
    message: str
    user: datamodels.UserModel = None


class AdminUserGetRequest(BaseModel):
    username: str


class AdminUserGetResponse(AdminUserCreateResponse):
    pass


class AdminUserUpdateRequest(BaseModel):
    username: str
    password: Optional[str] = None
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    quota: Optional[Dict[str, Any]] = None


class AdminUserUpdateResponse(AdminUserCreateResponse):
    pass


class AdminUserDeleteRequest(AdminUserGetRequest):
    pass


class AdminUserDeleteResponse(AdminUserCreateResponse):
    pass

class AdminTemplateCreateRequest(BaseModel):
    pass