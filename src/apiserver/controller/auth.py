import datetime
import http
from urllib.parse import urlparse, parse_qs

import jwt
from loguru import logger
from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi

from src.apiserver.controller.types import ResponseBaseModel
from src.apiserver.service import get_root_service
from src.apiserver.service.auth import LoginCredential, TokenResponse
from src.components import config
from src.components.datamodels import UserRoleEnum
from src.components.utils import parse_bearer

bp = Blueprint("auth", url_prefix="/auth", version=1)

_unauthorized_basic_response = json_response(
    body=ResponseBaseModel(
        description='',
        message='UNAUTHORIZED',
        status=http.HTTPStatus.UNAUTHORIZED
    ).model_dump(),
    headers={
        'WWW-Authenticate': "Basic realm=Auth Required"
    },
    status=http.HTTPStatus.UNAUTHORIZED
)

_authorized_basic_response = json_response(
    body=ResponseBaseModel(
        description='',
        message='AUTHORIZED',
        status=http.HTTPStatus.OK
    ).model_dump(),
    headers={
        'WWW-Authenticate': "Basic realm=Auth Required"
    },
    status=http.HTTPStatus.OK
)


def get_authorized_token_response(token: str):
    """
    This function returns an authorized response for token/validation endpoint
    It also sets a cookie config.CONFIG_AUTH_COOKIES_NAME=token
    """
    r = json_response(
        body=ResponseBaseModel(
            description='',
            message='AUTHORIZED',
            status=http.HTTPStatus.OK
        ).model_dump(),
        headers={
            'WWW-Authenticate': "Bearer"
        },
        status=http.HTTPStatus.OK
    )
    r.add_cookie(
        config.CONFIG_AUTH_COOKIES_NAME,
        token,
        max_age=config.CONFIG_DEVICE_TOKEN_EXPIRE_S
    )
    return r


def get_unauthorized_token_response():
    """
    This function returns an unauthorized response for token/validation endpoint
    It also deletes a the cookie config.CONFIG_AUTH_COOKIES_NAME
    """
    r = json_response(
        body=ResponseBaseModel(
            description='',
            message='UNAUTHORIZED',
            status=http.HTTPStatus.UNAUTHORIZED
        ).model_dump(),
        status=http.HTTPStatus.UNAUTHORIZED
    )
    r.delete_cookie(config.CONFIG_AUTH_COOKIES_NAME)
    return r


_bad_request_response = json_response(
    body=ResponseBaseModel(
        description='',
        status=http.HTTPStatus.BAD_REQUEST,
        message='BAD REQUEST',
    ).model_dump(),
    status=http.HTTPStatus.BAD_REQUEST
)


@bp.get("/basic/", name="basic", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": _authorized_basic_response}, status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_basic_response}, status=401
        ),
    ],
    secured={"token": []}
)
async def basic(request):
    """
    Basic auth for any user
    """

    # verify credential
    ret = await get_root_service().auth_service.basic(
        request.headers.authorization
    )
    if ret:
        return _authorized_basic_response
    else:
        return _unauthorized_basic_response


@bp.get("/basic/<username:str>", name="basic_user", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": _authorized_basic_response}, status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_basic_response}, status=401
        ),
    ],
    secured={"token": []}
)
async def basic_user(request, username: str):
    """
    Basic auth for specific user
    """

    # verify credential
    ret = await get_root_service().auth_service.basic(
        request.headers.authorization,
        username=username
    )
    if ret:
        return _authorized_basic_response
    else:
        return _unauthorized_basic_response


@bp.post("/token/login", name="token_login", version=1)
@openapi.definition(
    body={'application/json': LoginCredential.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {"application/json": TokenResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_basic_response}, status=401
        ),
    ],
)
async def token_login(request):
    """
    this is a hack to assign 10yr valid token to user
    """

    try:
        cred = LoginCredential(**request.json)
    except Exception as e:
        _ = e
        return _bad_request_response

    # verify credential
    access_token, err = await get_root_service().auth_service.token_login(cred)

    # return response
    if err is not None:
        return _unauthorized_basic_response
    else:
        return json_response(
            body=TokenResponse(
                description='',
                message='OK',
                status=http.HTTPStatus.OK,
                token=access_token
            ).model_dump(),
            status=http.HTTPStatus.OK
        )


@bp.post("/token/refresh", name="token_refresh", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": TokenResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_basic_response}, status=401
        ),
    ],
    secured={"token": []}
)
async def token_refresh(request):
    """
    this is a hack to verify the long-term token and sign short term token
    """
    # first check the presence of header
    old_token, err = parse_bearer(request.headers.authorization)
    if err is not None:
        return _unauthorized_basic_response

    # refresh token, pass JWT_SECRET
    access_token, err = await get_root_service().auth_service.user_token_refresh(
        old_token,
        request.app.config.get('JWT_SECRET')
    )

    # return response
    if err is not None:
        return _unauthorized_basic_response
    else:
        return json_response(
            body=TokenResponse(
                description='',
                message='OK',
                status=http.HTTPStatus.OK,
                token=access_token
            ).model_dump(),
            status=http.HTTPStatus.OK
        )


@bp.get("/token/validate/<username:str>", name="token_validate_user", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            status=200
        ),
        openapi.definitions.Response(
            {"application/json": get_unauthorized_token_response()}, status=401
        ),
    ],
    secured={"token": []}
)
async def token_validate(request, username: str):
    """
    This function validates the token in:
    - header.Authorization
    - urlParam.clpl_auth_token

    If the validation succeed, return 200 OK and set cookie clpl_auth_token=${JWT}
    """
    # try to get from cookies
    cookies_token = request.cookies.get(config.CONFIG_AUTH_COOKIES_NAME, None)
    if cookies_token is None:
        # cookie does not exists, fallback to header
        token, err = parse_bearer(request.headers.get('Authorization'))
        if err is not None:
            # header does not exists, fallback to query
            logger.debug(f"validation_err: {str(err)}, fallback to query")

            # attention: the proxy must pass the x-original-url header that contains original url
            origin_url = request.headers.get(config.CONFIG_PROXY_ORIGIN_URL_HEADER)
            if origin_url is None:
                logger.debug(f"validation_err: misconfigured proxy, no {config.CONFIG_PROXY_ORIGIN_URL_HEADER}")
                return get_unauthorized_token_response()
            else:
                result = parse_qs(urlparse(origin_url).query)
                token = result.get(config.CONFIG_AUTH_COOKIES_NAME, [None])[0]
                if token is None:
                    logger.debug(f"validation_err: {config.CONFIG_AUTH_COOKIES_NAME} not found in query")
                    return get_unauthorized_token_response()
    else:
        # succeed
        token = cookies_token

    # decode the jwt and check the signature
    try:
        payload = jwt.decode(
            token,
            request.app.config.get('JWT_SECRET'),
            algorithms=request.app.config.get('JWT_ALGORITHM')
        )
    except Exception as e:
        logger.debug(f"validation_err: {str(e)}")
        return get_unauthorized_token_response()

    # if user not match, return 401
    if payload['username'] != username:
        logger.debug(f"validation_err: expected user to be {username} but got {payload['username']}")
        return get_unauthorized_token_response()
    else:
        # replace the token with device token
        now = datetime.datetime.utcnow().timestamp()

        # rotate token if:
        # case 1: the token will expire in less than 6 days
        # case 2: the token is not device token
        if (
                (payload['exp'] < (now + config.CONFIG_DEVICE_TOKEN_RENEW_THRESHOLD_S)) or
                (payload['role'] != UserRoleEnum.device.value)
        ):
            logger.debug(f"validation_warning: token will expire in less "
                         f"than {config.CONFIG_DEVICE_TOKEN_RENEW_THRESHOLD_S} seconds, rotate token")
            payload['role'] = UserRoleEnum.device.value
            token, err = await get_root_service().auth_service.jwt_token_rotate(
                payload,
                request.app.config.get('JWT_SECRET'),
                datetime.timedelta(seconds=config.CONFIG_DEVICE_TOKEN_EXPIRE_S)
            )
            if err is not None:
                logger.debug(f"validation_err: {str(err)}")
                return get_unauthorized_token_response()

        # return authorized response
        logger.debug(f"validation_success")
        return get_authorized_token_response(token=token)
