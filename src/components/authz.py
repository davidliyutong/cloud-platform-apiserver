"""
Authorization Decorator
"""

import http
from functools import wraps
from typing import Iterable, Optional

import jwt
from loguru import logger
from sanic.response import json as json_response

from src.components.utils import parse_bearer


def validate_role(role: Optional[Iterable[str]] = None):
    """
    Authenticate User by JWT

    This decorator will check the JWT in the request header. Use its 'role' attribute to check the role.
    If the role is not matched, it will return 401.

    :param role: the role to check, set to None to skip the role check but add the user info to the request context
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            try:
                # header: Authorization: Bearer <jwt>s
                token, err = parse_bearer(request.headers.get('Authorization'))
                if err is not None:
                    raise err

                # decode the jwt and check the signature
                payload = jwt.decode(
                    token,
                    request.app.config.get('JWT_SECRET'),
                    algorithms=request.app.config.get('JWT_ALGORITHM')
                )

            except Exception as e:
                # logging the error
                logger.debug(str(e))
                return json_response(
                    {
                        'description': '',
                        'status': http.HTTPStatus.UNAUTHORIZED,
                        'message': str(e)
                    },
                    http.HTTPStatus.UNAUTHORIZED
                )

            # check the role
            if role is None or payload.get('role') in role:
                request.ctx.user = payload
                return await f(request, *args, **kwargs)
            else:
                error_msg = "Unauthorized"
                return json_response(
                    {
                        'description': '',
                        'status': http.HTTPStatus.UNAUTHORIZED,
                        'message': str(error_msg)
                    },
                    http.HTTPStatus.UNAUTHORIZED
                )

        return decorated_function

    return decorator
