import http
from functools import wraps
from sanic.response import json as json_response
import jwt
from typing import Iterable
from loguru import logger


def validate_role(role: Iterable[str]):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            error_msg = ""

            try:
                # Header: Authorization: Bearer <jwt>
                authorization_header = request.headers.get('Authorization').split(' ')
                if authorization_header is None:
                    error_msg = 'Authorization header is missing'
                    raise Exception(error_msg)
                authorization_header_split = request.headers.get('Authorization').split(' ')
                if len(authorization_header_split) != 2:
                    error_msg = 'Authorization header is malformed'
                    raise Exception(error_msg)

                token = authorization_header_split[1]

                # Verify the jwt, replace 'secret' with your Secret Key.
                try:
                    payload = jwt.decode(token, request.app.config.get('JWT_SECRET'), algorithms='HS256')
                    if payload.get('role') in role:
                        request.ctx.user = payload
                        return await f(request, *args, **kwargs)
                    else:
                        error_msg = "Unauthorized"
                        raise Exception(error_msg)
                except Exception as e:
                    raise Exception(error_msg)

            except Exception as e:
                # Logging the error can help you in debugging
                logger.exception(str(e))
                return json_response(
                    {
                        'description': '',
                        'status': http.HTTPStatus.UNAUTHORIZED,
                        'message': str(e)
                    },
                    http.HTTPStatus.UNAUTHORIZED
                )

        return decorated_function

    return decorator
