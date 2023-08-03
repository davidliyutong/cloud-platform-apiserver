import http

from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi

from src.apiserver.controller.types import ResponseBaseModel
from src.apiserver.service import get_root_service
from src.apiserver.service.auth import LoginCredential, TokenResponse

bp = Blueprint("auth", url_prefix="/auth", version=1)

_unauthorized_response = json_response(
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

_authorized_response = json_response(
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

_bad_request_response = json_response(
    body=ResponseBaseModel(
        description='',
        status=http.HTTPStatus.BAD_REQUEST,
        message='BAD REQUEST',
    ).model_dump(),
    status=http.HTTPStatus.BAD_REQUEST
)


@bp.get("/basic/", name="auth_basic", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": _authorized_response}, status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_response}, status=401
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
        return _authorized_response
    else:
        return _unauthorized_response


@bp.get("/basic/<username: str>", name="auth_basic_user", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": _authorized_response}, status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_response}, status=401
        ),
    ],
    secured={"token": []}
)
async def basic_user(request, username):
    """
    Basic auth for specific user
    """

    # verify credential
    ret = await get_root_service().auth_service.basic(
        request.headers.authorization,
        username=username
    )
    if ret:
        return _authorized_response
    else:
        return _unauthorized_response


@bp.post("/token/login", name="auth_token_login", version=1)
@openapi.definition(
    body={'application/json': LoginCredential.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {"application/json": TokenResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_response}, status=401
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
        return _unauthorized_response
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


@bp.post("/token/refresh", name="auth_token_refresh", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": TokenResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200
        ),
        openapi.definitions.Response(
            {"application/json": _unauthorized_response}, status=401
        ),
    ],
    secured={"token": []}
)
async def token_refresh(request):
    """
    this is a hack to verify the long-term token and sign short term token
    """

    # refresh token, pass JWT_SECRET
    access_token, err = await get_root_service().auth_service.token_refresh(
        request.headers.authorization,
        request.app.config.get('JWT_SECRET')
    )

    # return response
    if err is not None:
        return _unauthorized_response
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
