from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.components.types.common import ResponseBaseModel


class LoginCredential(BaseModel):
    username: str
    password: str
    otp_code: Optional[str] = None


class TokenResponse(ResponseBaseModel):
    token: str
    refresh_token: str = ''


class JWTTokenType(str, Enum):
    web: str = 'web'
    device: str = 'device'


class JWTTokenSchema(BaseModel):
    username: str
    type: JWTTokenType
    group: str
    exp: int
    iat: int
    email: str
    uuid: str


class RBACContextKeyEnum(str, Enum):
    rbac_id: str = 'rbac_id'
    rbac_group: str = 'rbac_group'


JWT_TOKEN_NAME = "token"
JWT_SECRET_KEYNAME = 'JWT_SECRET'
JWT_ALGORITHM_KEYNAME = 'JWT_ALGORITHM'
JWT_HEADER_NAME = 'Authorization'

POLICY_REFRESH_TOKEN_DURATION_SECOND = 60 * 60 * 24 * 30  # 30 days
POLICY_ACCESS_TOKEN_DURATION_SECOND = 60 * 60  # 1 hour
POLICY_DEVICE_TOKEN_EXPIRE_SECOND = 7 * 24 * 60 * 60  # 7 days
POLICY_DEVICE_TOKEN_RENEW_THRESHOLD_SECOND = 6 * 24 * 60 * 60  # 6 days


class JWTAuthenticationResponse(ResponseBaseModel):
    pass
