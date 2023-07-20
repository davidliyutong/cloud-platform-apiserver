import datetime
from typing import List

import src.components.datamodels as datamodels

from pydantic import BaseModel, field_serializer


class AuthJWTLoginRequest(BaseModel):
    username: str
    password: str


class AuthJWTLoginResponse(BaseModel):
    code: int
    expire: datetime.datetime
    token: str

    @field_serializer("expire")
    def serialize_expire(self, v: datetime.datetime, _info):
        return v.isoformat()


class AdminUserListRequest(BaseModel):
    uid_start: int = -1
    uid_end: int = -1
    extra_query_filter: str = ''


class AdminUserListResponse(BaseModel):
    code: int
    msg: str
    total_users: int = 0
    users: List[datamodels.UserModel] = []
