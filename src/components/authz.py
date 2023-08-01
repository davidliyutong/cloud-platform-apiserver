import http
from functools import wraps
from sanic.response import json as json_response
import jwt
from typing import Iterable, Optional
from loguru import logger

from src.components.utils import parse_bearer


def validate_role(role: Optional[Iterable[str]] = None):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            try:
                # Header: Authorization: Bearer <jwt>s
                token, err = parse_bearer(request.headers.get('Authorization'))
                if err is not None:
                    raise err

                # Verify the jwt, replace 'secret' with your Secret Key.
                payload = jwt.decode(
                    token,
                    request.app.config.get('JWT_SECRET'),
                    algorithms=request.app.config.get('JWT_ALGORITHM')
                )
                if role is None or payload.get('role') in role:
                    request.ctx.user = payload
                    return await f(request, *args, **kwargs)
                else:
                    error_msg = "Unauthorized"
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
