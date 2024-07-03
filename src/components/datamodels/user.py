import datetime
import re
import secrets
import uuid
from enum import Enum
from hashlib import sha256
from typing import Optional, List, Dict, Any, Self

import bcrypt
import pyotp
from odmantic import Model, Field
from pydantic import BaseModel, UUID4, EmailStr, SecretStr, field_validator, field_serializer

from src import CONFIG_BUILD_VERSION
from src.components.datamodels import user_collection_name
from src.components.datamodels.common import ResourceStatusEnum
from src.components.datamodels.group import GroupEnumInternal
from src.components.datamodels.quota import QuotaModelV2
from src.components.utils.security import get_hashed_text  #


class UserStatusEnum(str, Enum):
    """
    User status enum, used to define user status.
    """
    active = "active"
    inactive = "inactive"


class UserRoleEnum(str, Enum):
    """
    User role enum, used to define user roles
    """
    super_admin = "super_admin"
    admin = "admin"
    user = "user"
    device = "device"


class UserModelV2(Model):
    """
    User model v2, used to define user
    """
    model_config = {
        "collection": user_collection_name,
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.committed, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)
    username: str = Field(primary_field=True, index=True)
    group: str = Field(default=GroupEnumInternal.default)
    status: UserStatusEnum = Field(default=UserStatusEnum.active)
    email: Optional[EmailStr] = Field(default=None)
    password: SecretStr = Field(default=SecretStr(""))
    quota: Optional[QuotaModelV2] = Field(default=None)
    public_keys: List[str] = Field(default_factory=list)
    otp_secret: SecretStr = Field(default=SecretStr(""))
    otp_enabled: bool = Field(default=False)

    @field_validator("username")
    def username_must_be_valid(cls, v):
        pattern = '^[0-9a-zA-Z\-_]*$'
        if not re.match(pattern, v):
            raise ValueError("username must be alphanumeric")
        return v

    @field_serializer('password')
    def serialize_password(self, v: SecretStr, _info):
        return v.get_secret_value()

    @field_serializer('otp_secret')
    def serialize_otp_secret(self, v: SecretStr, _info):
        return v.get_secret_value()

    def challenge_password(self, plain_password: str) -> bool:
        password_hashed = sha256(str(plain_password).encode()).hexdigest()
        if secrets.compare_digest(
                password_hashed.encode('utf-8'),
                str(self.password.get_secret_value()).encode('utf-8')
        ):
            return True
        else:
            return False

    def challenge_otp_code(self, otp_code: str = ""):
        otp_code = otp_code or ""
        totp = pyotp.TOTP(self.otp_secret.get_secret_value())
        return totp.verify(otp_code, valid_window=1)
