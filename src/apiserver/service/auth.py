"""
This module implements auth related service
"""

import datetime
from typing import Tuple, Optional

import jwt
from loguru import logger
from odmantic import AIOEngine

from src.components.types import UserGetRequest
from src.components import errors
from src.components.datamodels import UserStatusEnum, UserModelV2
from src.components.utils import parse_basic
from src.components.auth.common import (
    LoginCredential,
    POLICY_REFRESH_TOKEN_DURATION_SECOND,
    POLICY_ACCESS_TOKEN_DURATION_SECOND, JWTTokenType
)

from .common import ServiceInterface
from src.components.utils.security import get_hashed_text


class AuthService(ServiceInterface):
    _algorithm = 'HS256'

    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self.engine = odm_engine

    @staticmethod
    def _get_payload_from_model(
            user: UserModelV2, duration: datetime.timedelta, token_type: JWTTokenType = JWTTokenType.web
    ):
        now = datetime.datetime.utcnow()
        return dict(
            type=token_type.value,
            username=user.username,
            group=user.group,
            exp=now + duration,
            iat=now,
            email=user.email,
            uuid=str(user.uuid)
        )

    @staticmethod
    def _get_renewed_token_payload(payload, duration: datetime.timedelta):
        now = datetime.datetime.utcnow()
        payload['exp'] = now + duration
        payload['iat'] = now
        return payload

    async def basic_login(self, app, auth_header: str, username: str = None) -> bool:
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
        user, err = await self.root_service.user_service.get(app, UserGetRequest(username=input_username))
        if any([
            err is not None,
            user is not None and user.status != UserStatusEnum.active,
        ]):
            return False

        # check password
        if user.challenge_password(input_password):
            return True
        else:
            return False

    async def jwt_token_login(self, app, cred: LoginCredential) -> Tuple[
        Optional[str], Optional[str], Optional[Exception]]:
        """
        Login with username and password, return a short-term jwt token for authn and long-term refresh token (jwt)
        """

        # verify user
        user: UserModelV2
        user, err = await self.root_service.user_service.get(app, UserGetRequest(username=cred.username))
        if err is not None:
            return None, None, err

        # check password
        if user.challenge_password(cred.password):
            if user.otp_enabled:
                if cred.otp_code is None:
                    return None, None, errors.otp_code_required
                if not user.challenge_otp_code(cred.otp_code):
                    return None, None, errors.otp_code_wrong

            # generate jwt
            refresh_payload = self._get_payload_from_model(
                user, datetime.timedelta(seconds=POLICY_REFRESH_TOKEN_DURATION_SECOND)
            )
            refresh_secret = get_hashed_text(
                self.root_service.opt.config_token_secret + user.password.get_secret_value().encode()
            )
            refresh_token = jwt.encode(refresh_payload, refresh_secret, algorithm=self._algorithm)

            access_secret = self.root_service.opt.config_token_secret
            access_payload = self._get_payload_from_model(
                user, datetime.timedelta(seconds=POLICY_ACCESS_TOKEN_DURATION_SECOND)
            )
            access_token = jwt.encode(access_payload, access_secret, algorithm=self._algorithm)

            return access_token, refresh_token, None
        else:
            return None, None, errors.wrong_password

    async def jwt_token_refresh(self, app, refresh_token: str) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Refresh user token, check with user's password generate short-term jwt token
        """

        # decode the jwt without verify, to get the user
        try:
            unverified_jwt = jwt.decode(refresh_token, options={"verify_signature": False})
            user, err = await self.root_service.user_service.get(
                app,
                UserGetRequest(username=unverified_jwt.get('username'))
            )
            if any([
                err is not None,
                user is not None and user.status != UserStatusEnum.active,
                user is not None and str(user.uuid) != str(unverified_jwt.get('uuid'))
            ]):
                return None, errors.user_not_found
        except Exception as e:
            logger.debug(str(e))
            return None, errors.invalid_token

        # verify the jwt using user's password hash
        try:
            _ = jwt.decode(
                refresh_token,
                get_hashed_text(self.root_service.opt.config_token_secret + user.password.get_secret_value().encode()),
                algorithms=self._algorithm
            )
        except Exception as e:
            logger.debug(str(e))
            return None, errors.invalid_token

        # sign new token using temporary secret, timeout is POLICY_ACCESS_TOKEN_DURATION_SECOND
        access_secret = self.root_service.opt.config_token_secret
        access_payload = self._get_payload_from_model(
            user, datetime.timedelta(seconds=POLICY_ACCESS_TOKEN_DURATION_SECOND)
        )
        access_token = jwt.encode(access_payload, access_secret, algorithm=self._algorithm)

        return access_token, None

    async def generate_oidc_token(
            self,
            user: UserModelV2,
            expire: Optional[datetime.timedelta] = None
    ) -> Tuple[str, Optional[Exception]]:
        """
        Generate jwt token for user, using global secret, used in OIDC login
        """
        if expire is None:
            expire = datetime.timedelta(seconds=self.root_service.opt.config_token_expire_s)

        # generate jwt
        payload = self._get_payload_from_model(user, expire)
        secret = self.root_service.opt.config_token_secret
        access_token = jwt.encode(payload, secret, algorithm=self._algorithm)

        return access_token, None

    async def jwt_token_rotate(self, payload, secret: str, duration: datetime.timedelta):
        """
        This method rotates jwt token, new token is signed with secret and will have duration = exp - iat
        """
        try:
            payload = self._get_renewed_token_payload(payload, duration)
            access_token = jwt.encode(payload, secret, algorithm=self._algorithm)
        except Exception as e:
            return None, e
        return access_token, None
