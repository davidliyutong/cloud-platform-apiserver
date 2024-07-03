import http

from sanic import Blueprint
from sanic_ext import openapi

from src.components.types.common import ResponseBaseModel
from src.apiserver.service import RootService
from src.components.utils.checkers import wrapped_model_response

bp = Blueprint("auth_basic", url_prefix="/auth/basic", version=1)

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


@bp.get("/", name="basic", version=1)
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


@bp.get("/<username:str>", name="basic_user", version=1)
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
