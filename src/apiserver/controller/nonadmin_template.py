"""
This module implements the non-admin template controller.
"""

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
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[
        openapi.definitions.Parameter("Authorization", str, location="header", required=True),
        openapi.definitions.Parameter("index_start", int, location="query", required=False),
        openapi.definitions.Parameter("index_end", int, location="query", required=False),
        openapi.definitions.Parameter("extra_query_filter", str, location="query", required=False)
    ]
)
@protected()
async def list(request):
    """
    List all templates. The same as admin_template_list, but without role check.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    if request.query_args is None:
        req = TemplateListRequest()
    else:
        req = TemplateListRequest(**{k: v for (k, v) in request.query_args})

    # list templates
    count, templates, err = await get_root_service().template_service.list(request.app, req)

    # return response
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
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[
        openapi.definitions.Parameter("Authorization", str, location="header", required=True),
    ]
)
@protected()
async def get(request, template_id: str):
    """
    Get a template by id. The same as admin_template_get, but without role check.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_id param in url
    if template_id is None or template_id == "":
        return json_response(
            TemplateGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        # get template
        req = TemplateGetRequest(template_id=template_id)
        template, err = await get_root_service().template_service.get(request.app, req)

        # return response
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
