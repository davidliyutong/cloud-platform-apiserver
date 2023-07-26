from sanic import Blueprint
import http
from abc import abstractmethod, ABCMeta
from typing import Union

from pydantic import BaseModel
from sanic import Sanic
from sanic.response import json as json_response
from .types import *
from sanic_ext import validate, openapi
from sanic_jwt import protected
from loguru import logger
from src.apiserver.service import service
from src.apiserver.repo import Repo, UserRepo
from src.components.config import BackendConfig
from src.components.logging import create_logger
import src.components.authn as authn
from ...components import errors

bp = Blueprint("admin_template", url_prefix="/admin/templates", version=1)


@bp.get("/", name="admin_template_list")
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    pass


@bp.post("/", name="admin_template_create")
@openapi.definition(
    body={'application/json': AdminTemplateCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    pass


@bp.get("/<templates_id:str>", name="admin_template_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, templates_id: str):
    pass


@bp.put("/<templates_id:str>", name="admin_template_update")
@openapi.definition(
    body={'application/json': AdminTemplateCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request):
    pass


@bp.delete("/<templates_id:str>", name="admin_template_delete")
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request):
    pass
