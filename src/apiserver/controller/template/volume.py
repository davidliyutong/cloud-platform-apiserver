# volume.py
"""
This module implements the volume template controller.
"""
import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

import src.components.errors as errors
from src.apiserver.service import RootService
from src.components.auth.common import JWT_TOKEN_NAME
from src.components.types.template import (
    VolumeTemplateListRequest, VolumeTemplateListResponse,
    VolumeTemplateCreateRequest, VolumeTemplateCreateResponse,
    VolumeTemplateGetRequest, VolumeTemplateGetResponse,
    VolumeTemplateUpdateRequest, VolumeTemplateUpdateResponse,
    VolumeTemplateDeleteRequest, VolumeTemplateDeleteResponse
)
from src.components.utils.checkers import unmarshal_json_request, unmarshal_query_args
from src.components.utils.wrappers import wrapped_model_response

from src.components.auth import authn, authz

bp = Blueprint("volume_template", url_prefix="/volume", version=1)


@bp.get("/<tag:str>/", name="volume_template_list_tag")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': VolumeTemplateListResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[
        openapi.definitions.Parameter("skip", int, location="query", required=False),
        openapi.definitions.Parameter("limit", int, location="query", required=False),
        openapi.definitions.Parameter("extra_query_filter", str, location="query", required=False)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="list",
    resource_fmts=["resources::/templates/volume/*", "resources::/templates/volume/{tag}/*"]
)
async def list_volume_templates(request, tag: str = "_"):
    """
    List all volume templates.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, VolumeTemplateListRequest, VolumeTemplateListResponse)
    if err is not None:
        return err_resp
    req.tag = tag

    # list templates
    count, res, err = await RootService().volume_template_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            VolumeTemplateListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            VolumeTemplateListResponse(status=http.HTTPStatus.OK, message="success", total_templates=count,
                                       templates=res)
        )


@bp.post("/", name="volume_template_create")
@openapi.definition(
    body={
        'application/json': VolumeTemplateCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")
    },
    response=[
        openapi.definitions.Response(
            {'application/json': VolumeTemplateCreateResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="create", resource_fmts=["resources::/templates/volume/*"])
async def create_volume_template(request):
    """
    Create a new volume template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, VolumeTemplateCreateRequest, VolumeTemplateCreateResponse)
    if err is not None:
        return err_resp

    # create template
    res, err = await RootService().volume_template_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            VolumeTemplateCreateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            VolumeTemplateCreateResponse(status=http.HTTPStatus.OK, message="success", template=res)
        )


@bp.get("/<tag:str>/<template_uuid:str>", name="volume_template_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': VolumeTemplateGetResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="read",
    resource_fmts=["resources::/templates/volume/*", "resources::/templates/volume/{tag}/*"]
)
async def get_volume_template(request, tag: str = "_", template_uuid: str = None):
    """
    Get a volume template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            VolumeTemplateGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # get template
        req = VolumeTemplateGetRequest(template_uuid=template_uuid)
        req.tag = tag

        res, err = await RootService().volume_template_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                VolumeTemplateGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return wrapped_model_response(
                VolumeTemplateGetResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


@bp.put("/<template_uuid:str>", name="volume_template_update")
@openapi.definition(
    body={
        'application/json': VolumeTemplateUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': VolumeTemplateUpdateResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="update", resource_fmts=["resources::/templates/volume/*"])
async def update_volume_template(request, template_uuid: str):
    """
    Update a volume template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            VolumeTemplateUpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        req, err_resp, err = unmarshal_json_request(request, VolumeTemplateUpdateRequest, VolumeTemplateUpdateResponse)
        if err is not None:
            return err_resp

        req.template_uuid = template_uuid  # set template_id to request

        # update template
        res, err = await RootService().volume_template_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                VolumeTemplateUpdateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                VolumeTemplateUpdateResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


@bp.delete("/<template_uuid:str>", name="volume_template_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': VolumeTemplateDeleteResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="delete", resource_fmts=["resources::/templates/volume/*"])
async def delete_volume_template(request, template_uuid: str):
    """
    Delete a volume template.

    This will delete the template. Volume created from this template will not be affected.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            VolumeTemplateDeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # delete template
        req = VolumeTemplateDeleteRequest(template_uuid=template_uuid)
        res, err = await RootService().volume_template_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                VolumeTemplateDeleteResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                VolumeTemplateDeleteResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


openapi.component(VolumeTemplateGetRequest)
openapi.component(VolumeTemplateGetResponse)
openapi.component(VolumeTemplateListRequest)
openapi.component(VolumeTemplateListResponse)
openapi.component(VolumeTemplateCreateRequest)
openapi.component(VolumeTemplateCreateResponse)
openapi.component(VolumeTemplateUpdateRequest)
openapi.component(VolumeTemplateUpdateResponse)
openapi.component(VolumeTemplateDeleteRequest)
openapi.component(VolumeTemplateDeleteResponse)
