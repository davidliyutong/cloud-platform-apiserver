import http
from sanic import Blueprint
from sanic.response import json as json_response
from sanic.response import text
from .types import *
from sanic_ext import openapi
from sanic_jwt import protected
from loguru import logger
from src.apiserver.service import service
from src.apiserver.repo import Repo, UserRepo
import src.components.authn as authn
from ...components import errors

bp = Blueprint("admin_template", url_prefix="/admin/templates", version=1)


@bp.get("/", name="admin_template_list")
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateListResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    return text("NotImplementedError")


@bp.post("/", name="admin_template_create")
@openapi.definition(
    body={'application/json': TemplateCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateCreateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    return text("NotImplementedError")


@bp.get("/<templates_id:str>", name="admin_template_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateGetResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, templates_id: str):
    return text("NotImplementedError")


@bp.put("/<templates_id:str>", name="admin_template_update")
@openapi.definition(
    body={'application/json': TemplateUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, templates_id: str):
    return text("NotImplementedError")


@bp.delete("/<templates_id:str>", name="admin_template_delete")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateDeleteResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, templates_id: str):
    return text("NotImplementedError")
