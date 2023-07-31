import http
import sanic
from sanic import Blueprint
from sanic.response import json as json_response
from sanic.response import text
from .types import (
    TemplateGetResponse,
    TemplateListRequest,
    TemplateListResponse,
)
from sanic_ext import openapi
from sanic_jwt import protected
from loguru import logger
from src.apiserver.service import service
from src.apiserver.repo import Repo, UserRepo
import src.components.authn as authn
from ...components import errors

bp = Blueprint("nonadmin_template", url_prefix="/templates", version=1)


@bp.get("/", name="template_list")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateListResponse.model_json_schema()})
@protected()
async def list(request):
    return text("NotImplementedError")


@bp.get("/<template_id:str>", name="template_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateGetResponse.model_json_schema()})
@protected()
async def get(request, template_id: str):
    return text("NotImplementedError")
