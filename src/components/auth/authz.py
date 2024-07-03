"""
Authorization Decorator
"""

import http
import itertools
from enum import Enum
from functools import wraps
from typing import Iterable, Optional, List

import jwt
from loguru import logger
from sanic.response import json as json_response

from src.apiserver.service import RootService
from src.components.auth.common import JWTAuthenticationResponse
from src.components.utils import parse_bearer
from src.components.utils.wrappers import wrapped_model_response


def validate_role_v1(role: Optional[Iterable[str]] = None):
    """
    Authorize User by JWT

    This decorator will check the JWT in the request header. Use its 'role' attribute to check the role.
    If the role is not matched, it will return 401.

    FIXME: deprecated

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


def enforce_rbac_any(subject_fmt: str = "{rbac_id}", action: str = "", resource_fmts: Optional[List[str]] = None):
    """
    Authorize User by JWT

    This decorator will check the JWT in the request header. Use its 'role' attribute to check the role.
    If the role is not matched, it will return 401.

    :param role: the role to check, set to None to skip the role check but add the user info to the request context
    """
    resource_fmts = resource_fmts or []
    action = action or ""

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            try:
                # must have rbac_id and rbac_group in the request context
                rbac_id = request.ctx.rbac_id
                rbac_group = request.ctx.rbac_group
                if rbac_id is None or rbac_group is None:
                    return wrapped_model_response(
                        JWTAuthenticationResponse(status=http.HTTPStatus.UNAUTHORIZED, message="")
                    )

                # kwargs is provided by sanic and contains the defined parameters
                values = kwargs | {'rbac_id': rbac_id, 'rbac_group': rbac_group}
                subjects = [subject_fmt.format(**values), rbac_group]
                resources = [resource_fmt.format(**values) for resource_fmt in resource_fmts]

                for subject, resource in itertools.product(subjects, resources):
                    result = await RootService().policy_service.enforce(
                        request.app,
                        subject, action, resource
                    )
                    if result:
                        return await f(request, *args, **kwargs)

                return wrapped_model_response(
                    JWTAuthenticationResponse(status=http.HTTPStatus.UNAUTHORIZED, message="Unauthorized")
                )

            except Exception as e:
                # logging the error
                logger.debug(str(e))
                return wrapped_model_response(
                    JWTAuthenticationResponse(status=http.HTTPStatus.UNAUTHORIZED, message=str(e))
                )

        return decorated_function

    return decorator
