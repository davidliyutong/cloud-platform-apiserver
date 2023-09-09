"""
This module implements auth related service
"""

import datetime
from typing import Tuple, Optional

import jwt
from loguru import logger
from pydantic import BaseModel

from src.apiserver.controller.types import ResponseBaseModel
from src.apiserver.repo import UserRepo
from src.apiserver.service import ServiceInterface
from src.components import errors
from src.components.datamodels import UserModel, UserStatusEnum
from src.components.utils import parse_basic


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
        if user.verify_password(input_password):
            return True
        else:
            return False

    async def token_login(self, cred: LoginCredential) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Login with username and password, return long-term jwt token
        """

        # verify user
        user, err = await self.parent.user_service.repo.get(cred.username)
        if err is not None:
            return None, err

        # check password
        if user.verify_password(cred.password):
            # generate jwt
            payload = self._get_payload(user, datetime.timedelta(days=3560))
            secret = user.htpasswd.get_secret_value().encode()
            access_token = jwt.encode(payload, secret, algorithm=self.algorithm)

            return access_token, None
        else:
            return None, errors.wrong_password

    async def generate_jwt_token(self,
                                 user: UserModel,
                                 expire: Optional[datetime.timedelta] = None) -> Tuple[str, Optional[Exception]]:
        """
        Generate jwt token for user, using global secret, used in OIDC login
        """
        if expire is None:
            expire = datetime.timedelta(seconds=self.parent.opt.config_token_expire_s)

        # generate jwt
        payload = self._get_payload(user, expire)
        secret = self.parent.opt.config_token_secret
        access_token = jwt.encode(payload, secret, algorithm=self.algorithm)

        return access_token, None

    async def user_token_refresh(self, old_token: str, secret: str) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Refresh token, check with user's htpasswd generate short-term jwt token
        """

        # decode the jwt without verify, to get the user
        try:
            unverified_jwt = jwt.decode(old_token, options={"verify_signature": False})
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

        # verify the jwt using user's htpasswd password hash
        try:
            _ = jwt.decode(
                old_token,
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

    async def jwt_token_rotate(self, payload, secret: str, duration: datetime.timedelta):
        """
        This method rotates jwt token, new token is signed with secret and will have duration = exp - iat
        """
        now = datetime.datetime.utcnow()
        try:
            new_payload = {
                'username': payload['username'],
                'exp': now + duration,
                'iat': now,
                'email': payload['email'],
                'role': payload['role'],
                'uid': payload['uid']
            }
        except Exception as e:
            return None, e
        access_token = jwt.encode(new_payload, secret, algorithm=self.algorithm)
        return access_token, None


from sanic_ext import openapi

# attention: registrate components
openapi.component(LoginCredential)
openapi.component(TokenResponse)
