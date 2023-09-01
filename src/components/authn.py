"""
Authentication module
"""
import base64
import secrets

from loguru import logger
from sanic import request, response
from sanic_jwt import Configuration, Responses, exceptions, Authentication

import src.components.datamodels as datamodels
import src.components.errors as errors
from src.apiserver.service import get_root_service


async def authenticate(req: request.Request):
    """
    Authenticate user by username and password
    """

    logger.debug(f"{req.path} invoked")
    username = req.json.get("username", None)
    password = req.json.get("password", None)

    if not username or not password:
        raise exceptions.AuthenticationFailed(str(errors.empty_username_or_password))

    # get user from database
    user, err = await get_root_service().user_service.repo.get(username)

    # check user status
    if user is None or user.status not in [datamodels.UserStatusEnum.active]:
        raise exceptions.AuthenticationFailed(str(err))
    else:
        # compare password
        if user.verify_password(password):
            return user.model_dump()
        else:
            raise exceptions.AuthenticationFailed(errors.wrong_password)


class MyJWTConfig(Configuration):
    # -------------- access token field name -------------------------
    access_token_name = "token"

    # -------------- authorization_header_prefix ---------------------
    # [Description] The prefix of the authorization header
    # [Default] 'Bearer:'
    authorization_header_prefix = "Bearer"

    # -------------- url_prefix ---------------------
    # [Description] Route address for obtaining authorization
    # [Default] '/auth'
    url_prefix = '/v1/auth/jwt'

    # -------------- path_to_authenticate ---------------------
    path_to_authenticate = '/login'
    path_to_refresh = '/refresh'

    # -------------- secret -------------------------
    # [Description] Encryption Password
    # [Default] 'This is a big secret. Shhhhh
    # [Suggestion] This password is the security core of JWT, it should be kept secret, and more complex passwords \
    # are recommended
    secret = base64.encodebytes(secrets.token_bytes(32))

    # -------------- expiration_delta ----------------------
    # [Description] Expiration time, in seconds
    # [Default] 30 minutes, that is: 60 * 30
    # [Suggestion] This time should not be too long, and it is recommended to enable refresh_token_enabled to \
    # automatically update the token
    expiration_delta = 60 * 60  # Changed to expire in 60 minutes

    # refresh_token_name = 'refresh_token'
    # refresh_token_enabled = True  # Enable refresh_token function

    # -------------- cookie_set ---------------------
    # [Description] Whether to write the obtained token information into the cookie
    # [Default] False, that is, do not write into cookies
    # Only when this item is True, other cookie-related settings will take effect.
    # cookie_set = True

    # -------------- cookie_access_token_name ---------------
    # [Description] The name of token stored in the cookie.
    # [Default] 'access_token'
    # cookie_access_token_name = "token"

    #  -------------- cookie_access_token_name ---------------
    # [Description] The key or attribute of the user object containing the user id, here corresponds to the unique \
    # identifier of the User class
    # [Default] 'user_id'
    user_id = "username"

    refresh_token_enabled = True  # Enable refresh_token function

    claim_iat = True  # Show issuance time, the default reserved field of JWT, not displayed by default in sanic-jwt


class MyJWTAuthentication(Authentication):
    async def retrieve_user(self, req, **kwargs):
        """
        Parse the user information from the payload, and then return the found user
        """
        user_id_attribute = self.config.user_id()
        if 'payload' in kwargs.keys():
            user_id = kwargs['payload'].get(user_id_attribute)
            user, err = await get_root_service().user_service.repo.get(user_id)
            if err is not None or user.status not in [datamodels.UserStatusEnum.active]:
                raise exceptions.AuthenticationFailed(str(err))
            else:
                return user.model_dump()
        else:
            raise exceptions.AuthenticationFailed(str(errors.invalid_token))

    # Extend payload
    async def extend_payload(self, payload, *args, **kwargs):
        """
        Some properties can be obtained from User and added to the payload
        Note: Payload information is public, do not add sensitive information here
        """

        user_id_attribute = self.config.user_id()  # should be 'username'
        user_id = payload.get(user_id_attribute)  # username of user
        user, _ = await get_root_service().user_service.repo.get(user_id)  # get user from database
        payload.update({'email': user.email, 'role': user.role, 'uid': user.uid})  # For example, add gender attribute
        return payload

    async def extract_payload(self, req, verify=True, *args, **kwargs):
        """
        Extract the payload from the request. (Do Nothing)
        """
        return await super().extract_payload(req, verify)


class MyJWTResponse(Responses):
    @staticmethod
    async def get_access_token_output(req, user, config, instance):
        """
        Get the output of the access_token. This will be the response of the login interface
        """
        access_token = await instance.ctx.auth.generate_access_token(user)

        output = {
            "description": "",
            "status": 200,
            "message": "success",
            config.access_token_name(): access_token
        }

        return access_token, output

    # Custom exception return information
    @staticmethod
    def exception_response(req: request.Request, exception: exceptions):
        """
        Exception types defined under sanic-jwt.exceptions:
        - AuthenticationFailed
        - MissingAuthorizationHeader
        - MissingAuthorizationCookie
        - InvalidAuthorizationHeader
        - MissingRegisteredClaim
        - Unauthorized
        """

        # No need to modify
        msg = str(exception)
        if exception.status_code == 500:
            msg = str(exception)
        elif isinstance(exception, exceptions.AuthenticationFailed):
            msg = str(exception)
        else:
            if "expired" in msg:
                msg = "authorization expired"
            else:
                msg = "unauthorized"
        result = {
            "code": exception.status_code,
            "msg": msg,
            "token": "",
        }
        return response.json(result, status=exception.status_code)


async def retrieve_refresh_token(*args, **kwargs):
    """
    Get the refresh_token from the request (Do Nothing)
    Notice: the refresh_token should be read in the database and compare with the one in the request. Here we just \
    return the refresh_token in the request and skip the comparison
    """
    req, user_id = kwargs['request'], kwargs['user_id']
    _ = f'refresh_token_{user_id}'
    token_str = req.json.get('refresh_token', None)
    if token_str is None:
        return b''
    else:
        return token_str.encode('utf-8')


async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
    """
    Store the refresh_token in the request (Do Nothing)
    Notice: the refresh_token should be stored in the database
    """
    _ = f'refresh_token_{user_id}={refresh_token}'
    return
