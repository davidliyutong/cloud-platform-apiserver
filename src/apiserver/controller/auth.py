import base64
import datetime
import http
import secrets
from hashlib import sha256

import jwt
from pydantic import BaseModel
from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi

from src.apiserver.controller.types import ResponseBaseModel
from src.apiserver.service import get_root_service
from src.components.datamodels import UserModel, UserStatusEnum
from src.components.utils import parse_basic, parse_bearer

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
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": _authorized_response})
@openapi.response(401, {"application/json": _unauthorized_response})
async def basic(request):
    username_password, err = parse_basic(request.headers.authorization)
    if err is not None:
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
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": _authorized_response})
@openapi.response(401, {"application/json": _unauthorized_response})
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


class LoginCredential(BaseModel):
    username: str
    password: str


class TokenResponse(ResponseBaseModel):
    token: str
    refresh_token: str = ''


_algorithm = 'HS256'


def _get_payload(user: UserModel, duration: datetime.timedelta):
    now = datetime.datetime.utcnow()
    return {
        'username': user.username,
        'exp': now + duration,
        'iat': now,
        'email': user.email,
        'role': user.role,
        'uid': user.uid
    }


@bp.post("/token/login", name="auth_token_login", version=1)
@openapi.definition(
    body={'application/json': LoginCredential.model_json_schema()},
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

    user, err = await get_root_service().user_service.repo.get(cred.username)
    if err is not None:
        return _unauthorized_response

    password_hashed = sha256(cred.password.encode()).hexdigest()
    if secrets.compare_digest(
            password_hashed.encode('utf-8'),
            str(user.password.get_secret_value()).encode('utf-8')
    ):

        payload = _get_payload(user, datetime.timedelta(days=3560))
        secret = request.app.config.CONFIG_TOKEN_SECRET
        access_token = jwt.encode(payload, secret, algorithm=_algorithm)

        return json_response(
            body=TokenResponse(
                description='',
                message='OK',
                status=http.HTTPStatus.OK,
                token=access_token
            ).model_dump(),
            status=http.HTTPStatus.OK
        )
    else:
        return _unauthorized_response


@bp.post("/token/refresh", name="auth_token_refresh", version=1)
@openapi.parameter("Authorization", str, location="header", required=True)
async def token_refresh(request):
    """
    this is a hack to verify the long-term token and sign short term token
    """
    token, err = parse_bearer(request.headers.get('Authorization'))
    if err is not None:
        raise err

    # Verify the jwt, replace 'secret' with your Secret Key.
    payload = jwt.decode(
        token,
        request.app.config.CONFIG_TOKEN_SECRET,
        algorithms=_algorithm
    )

    user, err = await get_root_service().user_service.repo.get(payload.get('username'))
    if err is not None or user.status != UserStatusEnum.active:
        return _unauthorized_response

    else:
        payload = _get_payload(user, datetime.timedelta(minutes=60))
        secret = request.app.config.get('JWT_SECRET')  #
        access_token = jwt.encode(payload, secret, algorithm=_algorithm)

        return json_response(
            body=TokenResponse(
                description='',
                message='OK',
                status=http.HTTPStatus.OK,
                token=access_token
            ).model_dump(),
            status=http.HTTPStatus.OK
        )
