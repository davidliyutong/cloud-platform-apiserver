import http

from loguru import logger
from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi
from sanic_jwt import protected

import src.components.authz as authn
import src.components.errors as errors
from src.apiserver.service import get_root_service
from .types import *

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
    logger.debug(f"{request.path} invoked")

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


@bp.post("/", name="admin_template_create")
@openapi.definition(
    body={'application/json': TemplateCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateCreateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    logger.debug(f"{request.path} invoked")

    if request.json is None:
        return json_response(
            TemplateCreateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        try:
            req = TemplateCreateRequest(**request.json)
        except Exception as e:
            return json_response(
                TemplateCreateResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )
        template, err = await get_root_service().template_service.create(request.app, req)

        if err is not None:
            return json_response(
                TemplateCreateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )

        else:
            return json_response(
                TemplateCreateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    template=template
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.get("/<template_id:str>", name="admin_template_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateGetResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, template_id: str):
    logger.debug(f"{request.path} invoked")

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


@bp.put("/<template_id:str>", name="admin_template_update")
@openapi.definition(
    body={'application/json': TemplateUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, template_id: str):
    logger.debug(f"{request.path} invoked")

    body = request.json
    if template_id is None or template_id == "":
        return json_response(
            UserUpdateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        body.update({"template_id": template_id})
        req = TemplateUpdateRequest(**body)
        template, err = await get_root_service().template_service.update(request.app, req)
        if err is not None:
            return json_response(
                TemplateUpdateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                TemplateUpdateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    template=template
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.delete("/<template_id:str>", name="admin_template_delete")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": TemplateDeleteResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, template_id: str):
    logger.debug(f"{request.path} invoked")

    if template_id is None or template_id == "":
        return json_response(
            TemplateDeleteResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = TemplateDeleteRequest(template_id=template_id)
        deleted_template, err = await get_root_service().template_service.delete(request.app, req)
        if err is not None:
            return json_response(
                TemplateDeleteResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                TemplateDeleteResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    template=deleted_template
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
