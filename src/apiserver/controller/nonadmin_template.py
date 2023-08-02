import http

from loguru import logger
from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi
from sanic_jwt import protected

import src.components.errors as errors
from src.apiserver.service import get_root_service
from .types import *

bp = Blueprint("nonadmin_template", url_prefix="/templates", version=1)


@bp.get("/", name="nonadmin_template_list")
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateListResponse.model_json_schema()})
@protected()
async def list(request):
    logger.debug(f"{request.method} {request.path} invoked")

    if request.query_args is None:
        req = TemplateListRequest()
    else:
        req = TemplateListRequest(**{k: v for (k, v) in request.query_args})
    count, templates, err = await get_root_service().template_service.list(request.app, req)

    if err is not None:
        return json_response(
            TemplateListResponse(
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(err)
            ).model_dump(),
            status=http.HTTPStatus.INTERNAL_SERVER_ERROR
        )
    else:
        return json_response(
            TemplateListResponse(
                status=http.HTTPStatus.OK,
                message="success",
                total_templates=count,
                templates=templates
            ).model_dump(),
            status=http.HTTPStatus.OK
        )


@bp.get("/<template_id:str>", name="nonadmin_template_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateGetResponse.model_json_schema()})
@protected()
async def get(request, template_id: str):
    logger.debug(f"{request.method} {request.path} invoked")

    if template_id is None or template_id == "":
        return json_response(
            TemplateGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = TemplateGetRequest(template_id=template_id)
        template, err = await get_root_service().template_service.get(request.app, req)
        if err is not None:
            return json_response(
                TemplateGetResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                TemplateGetResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    template=template
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
