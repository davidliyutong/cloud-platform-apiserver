"""
Authentication module
"""
import http
from functools import wraps

import jwt
from loguru import logger

from src.components.auth.common import (
    JWTTokenSchema,
    JWT_SECRET_KEYNAME,
    JWT_ALGORITHM_KEYNAME,
    JWT_HEADER_NAME,
    JWTAuthenticationResponse, JWTTokenType
)
from src.components.utils import parse_bearer
from src.components.utils.wrappers import wrapped_model_response


def protected(token_type: JWTTokenType = JWTTokenType.web):
    """
    Authenticate User by JWT

    This decorator will check the JWT in the request header.

    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            try:
                # header: Authorization: Bearer <jwt>s
                token, err = parse_bearer(request.headers.get(JWT_HEADER_NAME))
                if err is not None:
                    raise err

                # decode the jwt and check the signature
                payload: JWTTokenSchema = jwt.decode(
                    token,
                    request.app.config.get(JWT_SECRET_KEYNAME),
                    algorithms=request.app.config.get(JWT_ALGORITHM_KEYNAME)
                )

            except Exception as e:
                # logging the error
                logger.debug(str(e))
                return wrapped_model_response(
                    JWTAuthenticationResponse(status=http.HTTPStatus.UNAUTHORIZED, message=str(e))
                )

            if payload.get('type') != token_type.value:
                return wrapped_model_response(
                    JWTAuthenticationResponse(status=http.HTTPStatus.UNAUTHORIZED, message="Unauthorized")
                )

            # hooks for rbac
            request.ctx.rbac_id = f"user::{payload.get('username')}"
            request.ctx.rbac_group = f"group::{payload.get('group')}"

            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator
