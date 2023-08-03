"""
This module implements auth related service
"""

import datetime
import secrets
from hashlib import sha256
from typing import Tuple, Optional

import jwt
from loguru import logger
from pydantic import BaseModel

from src.apiserver.controller.types import ResponseBaseModel
from src.apiserver.repo import UserRepo
from src.apiserver.service import ServiceInterface
from src.components import errors
from src.components.datamodels import UserModel, UserStatusEnum
from src.components.utils import parse_basic, parse_bearer


class LoginCredential(BaseModel):
    username: str
    password: str


class TokenResponse(ResponseBaseModel):
    token: str
    refresh_token: str = ''


class AuthService(ServiceInterface):
    def __init__(self, user_repo: UserRepo):
        super().__init__()
        self.repo = user_repo
        self.algorithm = 'HS256'

    @staticmethod
    def _get_payload(user: UserModel, duration: datetime.timedelta):
        now = datetime.datetime.utcnow()
        return {
            'username': user.username,
            'exp': now + duration,
            'iat': now,
            'email': user.email,
            'role': user.role,
            'uid': user.uid
        }

    async def basic(self, auth_header: str, username: str = None) -> bool:
        """
        Basic auth
        """

        # parse auth header
        username_password, err = parse_basic(auth_header)
        if err is not None:
            return False
        input_username, input_password = username_password

        # if username is not None, check if username is the same as input_username
        if username is not None and username != input_username:
            return False
        user, err = await self.parent.user_service.repo.get(input_username)
        if any([
            err is not None,
            user is not None and user.status != UserStatusEnum.active,
        ]):
            return False

        # check password
        password_hashed = sha256(input_password.encode()).hexdigest()
        if secrets.compare_digest(
                password_hashed.encode('utf-8'),
                str(user.password.get_secret_value()).encode('utf-8')
        ):
            return True
        else:
            return True

    async def token_login(self, cred: LoginCredential) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Login with username and password, return long-term jwt token
        """

        # verify user
        user, err = await self.parent.user_service.repo.get(cred.username)
        if err is not None:
            return None, err

        # check password
        password_hashed = sha256(cred.password.encode()).hexdigest()
        if secrets.compare_digest(
                password_hashed.encode('utf-8'),
                str(user.password.get_secret_value()).encode('utf-8')
        ):
            # generate jwt
            payload = self._get_payload(user, datetime.timedelta(days=3560))
            secret = user.htpasswd.get_secret_value().encode()
            access_token = jwt.encode(payload, secret, algorithm=self.algorithm)

            return access_token, None
        else:
            return None, errors.wrong_password

    async def token_refresh(self, auth_header: str, secret) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Refresh token, generate short-term jwt token
        """

        token, err = parse_bearer(auth_header)
        if err is not None:
            return None, err

        # decode the jwt without verify, to get the user
        try:
            unverified_jwt = jwt.decode(token, options={"verify_signature": False})
            user, err = await self.parent.user_service.repo.get(unverified_jwt.get('username'))
            if any([
                err is not None,
                user is not None and user.status != UserStatusEnum.active,
                user is not None and user.uid != unverified_jwt.get('uid')
            ]):
                return None, errors.user_not_found
        except Exception as e:
            logger.debug(str(e))
            return None, errors.invalid_token

        # verify the jwt using user's password hash
        try:
            _ = jwt.decode(
                token,
                user.htpasswd.get_secret_value().encode(),
                algorithms=self.algorithm
            )
        except Exception as e:
            logger.debug(str(e))
            return None, errors.invalid_token

        # sign new token using temporary secret, timeout is 60 minutes
        payload = self._get_payload(user, datetime.timedelta(minutes=60))
        access_token = jwt.encode(payload, secret, algorithm=self.algorithm)

        return access_token, None
