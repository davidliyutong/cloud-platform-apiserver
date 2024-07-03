# template.py
"""
This module implements the template controller.
"""

# TODO: test the apis

import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

import src.components.auth.authn as authn
import src.components.auth.common
import src.components.errors as errors
from src.apiserver.service import RootService
from src.components.types.template import TemplateListRequest, TemplateListResponse, TemplateCreateRequest, \
    TemplateCreateResponse, TemplateGetRequest, TemplateGetResponse, TemplateUpdateRequest, TemplateUpdateResponse, \
    TemplateDeleteRequest, TemplateDeleteResponse
from src.components.utils.checkers import unmarshal_json_request, unmarshal_query_args
from src.components.utils.wrappers import wrapped_model_response
from src.components.auth import authn, authz


bp = Blueprint("template", url_prefix="/template", version=1)


@bp.get("/", name="template_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[
        openapi.definitions.Parameter("skip", int, location="query", required=False),
        openapi.definitions.Parameter("limit", int, location="query", required=False),
        openapi.definitions.Parameter("extra_query_filter", str, location="query", required=False)
    ],
    secured={src.components.auth.common.JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="list", resource_fmts=["resources::/templates/*"])
async def list_templates(request):
    """
    List all templates.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, TemplateListRequest, TemplateListResponse)
    if err is not None:
        return err_resp

    # list templates
    count, res, err = await RootService().template_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            TemplateListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            TemplateListResponse(status=http.HTTPStatus.OK, message="success", total_templates=count, templates=res)
        )


@bp.post("/", name="template_create")
@openapi.definition(
    body={'application/json': TemplateCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateCreateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@authn.protected()
@authz.enforce_rbac_any(action="create", resource_fmts=["resources::/templates/*"])
async def create_template(request):
    """
    Create a new template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, TemplateCreateRequest, TemplateCreateResponse)
    if err is not None:
        return err_resp

    # create template
    res, err = await RootService().template_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            TemplateCreateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            TemplateCreateResponse(status=http.HTTPStatus.OK, message="success", template=res)
        )


@bp.get("/<template_uuid:str>", name="template_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@authn.protected()
@authz.enforce_rbac_any(action="read", resource_fmts=["resources::/templates/*"])
async def get_template(request, template_uuid: str):
    """
    Get a template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            TemplateGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # get template
        req = TemplateGetRequest(template_uuid=template_uuid)
        res, err = await RootService().template_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                TemplateGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return wrapped_model_response(
                TemplateGetResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


@bp.put("/<template_uuid:str>", name="template_update")
@openapi.definition(
    body={'application/json': TemplateUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateUpdateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
)
@authn.protected()
@authz.enforce_rbac_any(action="update", resource_fmts=["resources::/templates/*"])
async def update_template(request, template_uuid: str):
    """
    Update a template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            TemplateUpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        req, err_resp, err = unmarshal_json_request(request, TemplateUpdateRequest, TemplateUpdateResponse)
        if err is not None:
            return err_resp

        req.template_uuid = template_uuid  # set template_id to request

        # update template
        res, err = await RootService().template_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                TemplateUpdateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                TemplateUpdateResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


@bp.delete("/<template_uuid:str>", name="template_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': TemplateDeleteResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
)
@authn.protected()
@authz.enforce_rbac_any(action="delete", resource_fmts=["resources::/templates/*"])
async def delete_template(request, template_uuid: str):
    """
    Delete a template.

    This will delete the template. Pod created from this template will not be affected.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            TemplateDeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # delete template
        req = TemplateDeleteRequest(template_uuid=template_uuid)
        res, err = await RootService().template_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                TemplateDeleteResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                TemplateDeleteResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


openapi.component(TemplateGetRequest)
openapi.component(TemplateGetResponse)
openapi.component(TemplateListRequest)
openapi.component(TemplateListResponse)
openapi.component(TemplateCreateRequest)
openapi.component(TemplateCreateResponse)
openapi.component(TemplateUpdateRequest)
openapi.component(TemplateUpdateResponse)
openapi.component(TemplateDeleteRequest)
openapi.component(TemplateDeleteResponse)
