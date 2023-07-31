import base64
import http
import secrets
from hashlib import sha256

from sanic import Blueprint
from sanic.response import json as json_response

from src.apiserver.service import get_root_service

bp = Blueprint("auth", url_prefix="/auth", version=1)

_unauthorized_response = json_response(
    body={
        'description': '',
        'message': 'UNAUTHORIZED',
        'status': http.HTTPStatus.UNAUTHORIZED
    },
    headers={
        'WWW-Authenticate': "Basic realm=Auth Required"
    },
    status=http.HTTPStatus.UNAUTHORIZED
)

_authorized_response = json_response(
    body={
        'description': '',
        'message': 'AUTHORIZED',
        'status': http.HTTPStatus.OK
    },
    status=http.HTTPStatus.OK
)


@bp.get("/basic/", name="auth_basic", version=1)
async def basic(request):
    basic_auth_split = request.headers.authorization.split('Basic ')
    if len(basic_auth_split) < 2:
        return _unauthorized_response
    basic_auth = str(base64.b64decode(basic_auth_split[-1]), encoding='utf-8')
    username_password = basic_auth.split(':')
    if len(username_password) < 2:
        return _unauthorized_response

    username, password = username_password
    user, err = await get_root_service().user_service.repo.get(username)
    if err is not None:
        return _unauthorized_response

    password_hashed = sha256(password.encode()).hexdigest()
    if secrets.compare_digest(
        password_hashed.encode('utf-8'),
        str(user.password.get_secret_value()).encode('utf-8')
    ):
        return _authorized_response
    else:
        return _unauthorized_response


@bp.get("/basic/<username: str>", name="auth_basic_user", version=1)
async def basic_user(request, username):
    basic_auth_split = request.headers.authorization.split('Basic ')
    if len(basic_auth_split) < 2:
        return _unauthorized_response
    basic_auth = str(base64.b64decode(basic_auth_split[-1]), encoding='utf-8')
    username_password = basic_auth.split(':')
    if len(username_password) < 2:
        return _unauthorized_response

    input_username, input_password = username_password
    if input_username != username:
        return _unauthorized_response

    user, err = await get_root_service().user_service.repo.get(input_username)
    if err is not None:
        return _unauthorized_response

    password_hashed = sha256(input_password.encode()).hexdigest()
    if secrets.compare_digest(
        password_hashed.encode('utf-8'),
        str(user.password.get_secret_value()).encode('utf-8')
    ):
        return _authorized_response
    else:
        return _unauthorized_response
