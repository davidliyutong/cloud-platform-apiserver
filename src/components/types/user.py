from typing import List, Optional, Dict, Any

from pydantic import field_serializer, SecretStr, BaseModel, EmailStr, field_validator

from src.components.datamodels import UserModelV2, QuotaModelV2, UserStatusEnum
from src.components.datamodels.group import GroupEnumInternal
from src.components.types.common import _ensure_non_empty_value, ListRequestBaseModel, ResponseBaseModel


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
