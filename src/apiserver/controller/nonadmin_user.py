import http
import sanic
from sanic import Blueprint
from sanic.response import json as json_response
from sanic.response import text
from sanic.response import text
from .types import (
    UserGetResponse,
    UserUpdateResponse,
)
from sanic_ext import openapi
from sanic_jwt import protected
from loguru import logger
from src.apiserver.service import service
from src.apiserver.repo import Repo, UserRepo
import src.components.authn as authn
from ...components import errors

bp = Blueprint("nonadmin_user", url_prefix="/users", version=1)


@bp.get("/<username>", name="user_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserGetResponse.model_json_schema()})
@protected()
async def get(request, username: str):
    return text("NotImplementedError")


@bp.put("/<username>", name="user_update")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserUpdateResponse.model_json_schema()})
@protected()
async def update(request, username: str):
    return text("NotImplementedError")
