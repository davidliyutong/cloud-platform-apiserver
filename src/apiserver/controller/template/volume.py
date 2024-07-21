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

from src.components.types.template import VolumeTemplateListRequest as ListRequest
from src.components.types.template import VolumeTemplateListResponse as ListResponse
from src.components.types.template import VolumeTemplateCreateRequest as CreateRequest
from src.components.types.template import VolumeTemplateCreateResponse as CreateResponse
from src.components.types.template import VolumeTemplateGetRequest as GetRequest
from src.components.types.template import VolumeTemplateGetResponse as GetResponse
from src.components.types.template import VolumeTemplateUpdateRequest as UpdateRequest
from src.components.types.template import VolumeTemplateUpdateResponse as UpdateResponse
from src.components.types.template import VolumeTemplateDeleteRequest as DeleteRequest
from src.components.types.template import VolumeTemplateDeleteResponse as DeleteResponse
from src.components.utils.checkers import unmarshal_json_request, unmarshal_query_args
from src.components.utils.wrappers import wrapped_model_response as wrapped

from src.components.auth import authn, authz

bp = Blueprint("volume_template", url_prefix="/volume", version=1)


@bp.get("/", name="volume_template_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': ListResponse.model_json_schema(
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
async def list_volume_templates(request, tag: str = "_"):
    """
    List all volume templates.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, ListRequest, ListResponse)
    if err is not None:
        return err_resp

    # list templates
    count, res, err = await RootService().volume_template_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped(ListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err)))
    else:
        return wrapped(ListResponse(status=http.HTTPStatus.OK, message="success", total_templates=count, templates=res))


@bp.post("/", name="volume_template_create")
@openapi.definition(
    body={
        'application/json': CreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")
    },
    response=[
        openapi.definitions.Response(
            {'application/json': CreateResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
async def create_volume_template(request):
    """
    Create a new volume template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, CreateRequest, CreateResponse)
    if err is not None:
        return err_resp

    # create template
    res, err = await RootService().volume_template_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped(CreateResponse(status=err.code, message=str(err)))
    else:
        return wrapped(CreateResponse(status=http.HTTPStatus.OK, message="success", template=res))


@bp.get("/<template_uuid:str>", name="volume_template_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': GetResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
async def get_volume_template(request, template_uuid: str = None):
    """
    Get a volume template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped(GetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body)))
    else:
        # get template
        req = GetRequest(
            rbac_username=request.ctx.username,
            rbac_group_name=request.ctx.group_name,
            template_uuid=template_uuid
        )

        res, err = await RootService().volume_template_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped(GetResponse(status=err.code, message=str(err)))
        else:
            return wrapped(GetResponse(status=http.HTTPStatus.OK, message="success", template=res))


@bp.put("/<template_uuid:str>", name="volume_template_update")
@openapi.definition(
    body={
        'application/json': UpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': UpdateResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
async def update_volume_template(request, template_uuid: str):
    """
    Update a volume template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template param in url
    if template_uuid is None or template_uuid == "":
        return wrapped(UpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body)))
    else:
        req, err_resp, err = unmarshal_json_request(request, UpdateRequest, UpdateResponse)
        if err is not None:
            return err_resp

        req.template_uuid = template_uuid  # set template_id to request

        # update template
        res, err = await RootService().volume_template_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped(UpdateResponse(status=err.code, message=str(err)))
        else:
            return wrapped(UpdateResponse(status=http.HTTPStatus.OK, message="success", template=res))


@bp.delete("/<template_uuid:str>", name="volume_template_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': DeleteResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
async def delete_volume_template(request, template_uuid: str):
    """
    Delete a volume template.

    This will delete the template. Volume created from this template will not be affected.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped(DeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body)))
    else:
        # delete template
        req = DeleteRequest(
            rbac_username=request.ctx.username,
            rbac_group_name=request.ctx.group_name,
            template_uuid=template_uuid
        )
        res, err = await RootService().volume_template_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped(DeleteResponse(status=err.code, message=str(err)))
        else:
            return wrapped(DeleteResponse(status=http.HTTPStatus.OK, message="success", template=res))


openapi.component(GetRequest)
openapi.component(GetResponse)
openapi.component(ListRequest)
openapi.component(ListResponse)
openapi.component(CreateRequest)
openapi.component(CreateResponse)
openapi.component(UpdateRequest)
openapi.component(UpdateResponse)
openapi.component(DeleteRequest)
openapi.component(DeleteResponse)
