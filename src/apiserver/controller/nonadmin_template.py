"""
This module implements the non-admin template controller.
"""

import http
import json

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
        openapi.definitions.Parameter("index_start", int, location="query", required=False),
        openapi.definitions.Parameter("index_end", int, location="query", required=False),
        openapi.definitions.Parameter("extra_query_filter", str, location="query", required=False)
    ],
    secured={"token": []}
)
@protected()
async def list(request):
    """
    List all enabled templates. Disabled templates are hidden from non-admin users.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    args = {k: v for (k, v) in request.query_args}

    # Merge caller-supplied filter with the enabled constraint so disabled
    # templates are never visible to non-admin users.
    user_filter = {}
    if args.get("extra_query_filter", ""):
        try:
            user_filter = json.loads(args["extra_query_filter"])
        except json.JSONDecodeError:
            return json_response(
                TemplateListResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(errors.wrong_query_filter)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )

    # {"enabled": {"$ne": False}} matches both explicit True and legacy docs
    # that pre-date the enabled field (treated as enabled by default).
    merged_filter = {"enabled": {"$ne": False}, **user_filter}
    args["extra_query_filter"] = json.dumps(merged_filter)

    req = TemplateListRequest(**args)

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
    secured={"token": []}
)
@protected()
async def get(request, template_id: str):
    """
    Get a template by id. Returns 404 for disabled templates.
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
        elif not template.enabled:
            return json_response(
                TemplateGetResponse(
                    status=http.HTTPStatus.NOT_FOUND,
                    message=str(errors.template_not_found)
                ).model_dump(),
                status=http.HTTPStatus.NOT_FOUND
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
