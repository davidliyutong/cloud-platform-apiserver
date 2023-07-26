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

bp = Blueprint("admin_pod", url_prefix="/admin/pods", version=1)


@bp.get("/", name="admin_pod_list")
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodListResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    return text("NotImplementedError")


@bp.post("/", name="admin_pod_create")
@openapi.definition(
    body={'application/json': PodCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodCreateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    return text("NotImplementedError")


@bp.get("/<pod_id:str>", name="admin_pod_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodGetResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, pod_id: str):
    return text("NotImplementedError")


@bp.put("/<pod_id:str>", name="admin_pod_update")
@openapi.definition(
    body={'application/json': PodUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, pod_id: str):
    return text("NotImplementedError")


@bp.delete("/<pod_id:str>", name="admin_pod_delete")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodDeleteResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, pod_id: str):
    return text("NotImplementedError")
