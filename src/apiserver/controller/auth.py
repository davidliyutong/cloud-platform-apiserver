import datetime
import http
from urllib.parse import urlparse, parse_qs

import jwt
from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

from src.components.types import ResponseBaseModel
from src.apiserver.service import RootService
from src.components.auth.common import LoginCredential, TokenResponse, JWT_SECRET_KEYNAME, JWT_HEADER_NAME, \
    JWT_ALGORITHM_KEYNAME, JWTTokenType, POLICY_DEVICE_TOKEN_RENEW_THRESHOLD_SECOND, POLICY_DEVICE_TOKEN_EXPIRE_SECOND, \
    JWTTokenSchema
from src.components import config
from src.components.datamodels import UserRoleEnum
from src.components.utils.parser import parse_bearer
from src.components.utils.checkers import wrapped_model_response

bp = Blueprint("auth", url_prefix="/auth", version=1)

_unauthorized_basic_response = wrapped_model_response(
    ResponseBaseModel(message='UNAUTHORIZED', status=http.HTTPStatus.UNAUTHORIZED),
    headers={'WWW-Authenticate': "Basic realm=Auth Required"},
)

_authorized_basic_response = wrapped_model_response(
    ResponseBaseModel(message='AUTHORIZED', status=http.HTTPStatus.OK),
    headers={'WWW-Authenticate': "Basic realm=Auth Required"},
)

_bad_request_response = wrapped_model_response(
    ResponseBaseModel(message='BAD_REQUEST', status=http.HTTPStatus.BAD_REQUEST),
)


def get_authorized_token_response(token: str):
    """
    This function returns an authorized response for token/validation endpoint
    It also sets a cookie config.CONFIG_AUTH_COOKIES_NAME=token
    """
    r = wrapped_model_response(
        ResponseBaseModel(message='AUTHORIZED', status=http.HTTPStatus.OK),
        headers={'WWW-Authenticate': "Bearer"},
    )
    r.add_cookie(
        config.CONFIG_AUTH_COOKIES_NAME,
        token,
        max_age=POLICY_DEVICE_TOKEN_EXPIRE_SECOND
    )
    return r


def get_unauthorized_token_response():
    """
    This function returns an unauthorized response for token/validation endpoint
    It also deletes the cookie config.CONFIG_AUTH_COOKIES_NAME
    """
    r = wrapped_model_response(
        ResponseBaseModel(message='UNAUTHORIZED', status=http.HTTPStatus.UNAUTHORIZED),
    )
    r.delete_cookie(config.CONFIG_AUTH_COOKIES_NAME)
    return r


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
    secured={"http_basic": []}
)
async def basic_all(request):
    """
    Basic auth for any user
    """

    # verify credential
    ret = await RootService().auth_service.basic_login(request.app, request.headers.authorization)
    return _authorized_basic_response if ret else _unauthorized_basic_response


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
    secured={"http_basic": []}
)
async def basic_user(request, username: str):
    """
    Basic auth for specific user
    """

    # verify credential
    ret = await RootService().auth_service.basic_login(
        request.app,
        request.headers.authorization,
        username=username
    )
    return _authorized_basic_response if ret else _unauthorized_basic_response


@bp.post("/jwt/login", name="jwt_token_login", version=1)
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
async def jwt_token_login(request):
    """
    JWT Token login with credential
    """

    try:
        cred = LoginCredential(**request.json)
    except Exception as e:
        _ = e
        return _bad_request_response

    # verify credential
    access_token, refresh_token, err = await RootService().auth_service.jwt_token_login(request.app, cred)

    # return response
    if err is not None:
        return _unauthorized_basic_response
    else:
        return wrapped_model_response(
            TokenResponse(message='OK', status=http.HTTPStatus.OK, token=access_token, refresh_token=refresh_token),
        )


@bp.post("/jwt/refresh", name="jwt_token_refresh", version=1)
@openapi.definition(
    parameter=[
        openapi.definitions.Parameter(
            name="Authorization",
            location="header",
        )
    ],
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
async def jwt_token_refresh(request):
    """
    JWT Token refresh with a long-term token
    """

    # first check the presence of header
    refresh_token, err = parse_bearer(request.headers.authorization)
    if err is not None:
        return _unauthorized_basic_response

    # refresh token, pass JWT_SECRET
    access_token, err = await RootService().auth_service.jwt_token_refresh(
        request.app,
        refresh_token,
    )

    # return response
    if err is not None:
        return _unauthorized_basic_response
    else:
        return wrapped_model_response(
            TokenResponse(message='OK', status=http.HTTPStatus.OK, token=access_token),
        )


@bp.get("/token/validate/<username:str>", name="token_validate_user", version=1)
@bp.get("/jwt/validate/<username:str>", name="jwt_token_validate_user", version=1)
@openapi.definition(
    parameter=[
        openapi.definitions.Parameter(
            name=JWT_HEADER_NAME,
            location="header",
        )
    ],
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
async def jwt_token_validate(request, username: str):
    """
    JWT Token validation endpoint.
    """

    # note: This function validates the token in:
    #  - header.Authorization
    #  - urlParam.{{ CONFIG_AUTH_COOKIES_NAME }}
    #
    #  If the validation succeed, return 200 OK and set cookie {{ CONFIG_AUTH_COOKIES_NAME }}=${JWT}

    # try to get from cookies
    cookies_token = request.cookies.get(config.CONFIG_AUTH_COOKIES_NAME, None)
    if cookies_token is None:
        # cookie does not exists, fallback to header
        token, err = parse_bearer(request.headers.get(JWT_HEADER_NAME))
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
        payload: JWTTokenSchema = jwt.decode(
            token,
            request.app.config.get(JWT_SECRET_KEYNAME),
            algorithms=request.app.config.get(JWT_ALGORITHM_KEYNAME)
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
                (payload['exp'] < (now + POLICY_DEVICE_TOKEN_RENEW_THRESHOLD_SECOND)) or
                (payload['type'] != JWTTokenType.device.value)
        ):
            logger.debug(f"validation_notice: token will expire in less "
                         f"than {POLICY_DEVICE_TOKEN_RENEW_THRESHOLD_SECOND} seconds, rotate token")
            payload['type'] = UserRoleEnum.device.value
            token, err = await RootService().auth_service.jwt_token_rotate(
                payload,
                request.app.config.get(JWT_SECRET_KEYNAME),
                datetime.timedelta(seconds=POLICY_DEVICE_TOKEN_EXPIRE_SECOND)
            )
            if err is not None:
                logger.debug(f"validation_err: {str(err)}")
                return get_unauthorized_token_response()

        # return authorized response
        logger.debug(f"validation_success")
        return get_authorized_token_response(token=token)


openapi.component(LoginCredential)
openapi.component(TokenResponse)
