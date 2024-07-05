# pod.py
"""
This module implements the pod template controller.
"""
import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

import src.components.errors as errors
from src.apiserver.service import RootService
from src.components.auth.common import JWT_TOKEN_NAME
from src.components.types.template import (
    PodTemplateListRequest, PodTemplateListResponse,
    PodTemplateCreateRequest, PodTemplateCreateResponse,
    PodTemplateGetRequest, PodTemplateGetResponse,
    PodTemplateUpdateRequest, PodTemplateUpdateResponse,
    PodTemplateDeleteRequest, PodTemplateDeleteResponse
)
from src.components.utils.checkers import unmarshal_json_request, unmarshal_query_args
from src.components.utils.wrappers import wrapped_model_response

from src.components.auth import authn, authz

bp = Blueprint("pod_template", url_prefix="/pod", version=1)


@bp.get("/<tag:str>/", name="pod_template_list_tag")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PodTemplateListResponse.model_json_schema(
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
    resource_fmts=["resources::/templates/pod/*", "resources::/templates/pod/{tag}/*"]
)
async def list_pod_templates(request, tag: str = "_"):
    """
    List all pod templates.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, PodTemplateListRequest, PodTemplateListResponse)
    if err is not None:
        return err_resp
    req.tag = tag

    # list templates
    count, res, err = await RootService().pod_template_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            PodTemplateListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            PodTemplateListResponse(status=http.HTTPStatus.OK, message="success", total_templates=count, templates=res)
        )


@bp.post("/", name="pod_template_create")
@openapi.definition(
    body={
        'application/json': PodTemplateCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")
    },
    response=[
        openapi.definitions.Response(
            {'application/json': PodTemplateCreateResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="create", resource_fmts=["resources::/templates/pod/*"])
async def create_pod_template(request):
    """
    Create a new pod template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, PodTemplateCreateRequest, PodTemplateCreateResponse)
    if err is not None:
        return err_resp

    # create template
    res, err = await RootService().pod_template_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            PodTemplateCreateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            PodTemplateCreateResponse(status=http.HTTPStatus.OK, message="success", template=res)
        )


@bp.get("/<tag:str>/<template_uuid:str>", name="pod_template_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PodTemplateGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="read",
    resource_fmts=["resources::/templates/pod/*", "resources::/templates/pod/{tag}/*"]
)
async def get_pod_template(request, tag: str = "_", template_uuid: str = None):
    """
    Get a pod template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            PodTemplateGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # get template
        req = PodTemplateGetRequest(template_uuid=template_uuid)
        req.tag = tag

        res, err = await RootService().pod_template_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                PodTemplateGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return wrapped_model_response(
                PodTemplateGetResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


@bp.put("/<template_uuid:str>", name="pod_template_update")
@openapi.definition(
    body={'application/json': PodTemplateUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': PodTemplateUpdateResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="update", resource_fmts=["resources::/templates/pod/*"])
async def update_pod_template(request, template_uuid: str):
    """
    Update a pod template.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            PodTemplateUpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        req, err_resp, err = unmarshal_json_request(request, PodTemplateUpdateRequest, PodTemplateUpdateResponse)
        if err is not None:
            return err_resp

        req.template_uuid = template_uuid  # set template_id to request

        # update template
        res, err = await RootService().pod_template_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                PodTemplateUpdateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                PodTemplateUpdateResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


@bp.delete("/<template_uuid:str>", name="pod_template_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PodTemplateDeleteResponse.model_json_schema(
                ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="delete", resource_fmts=["resources::/templates/pod/*"])
async def delete_pod_template(request, template_uuid: str):
    """
    Delete a pod template.

    This will delete the template. Pod created from this template will not be affected.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check template_uuid param in url
    if template_uuid is None or template_uuid == "":
        return wrapped_model_response(
            PodTemplateDeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # delete template
        req = PodTemplateDeleteRequest(template_uuid=template_uuid)
        res, err = await RootService().pod_template_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                PodTemplateDeleteResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                PodTemplateDeleteResponse(status=http.HTTPStatus.OK, message="success", template=res)
            )


openapi.component(PodTemplateGetRequest)
openapi.component(PodTemplateGetResponse)
openapi.component(PodTemplateListRequest)
openapi.component(PodTemplateListResponse)
openapi.component(PodTemplateCreateRequest)
openapi.component(PodTemplateCreateResponse)
openapi.component(PodTemplateUpdateRequest)
openapi.component(PodTemplateUpdateResponse)
openapi.component(PodTemplateDeleteRequest)
openapi.component(PodTemplateDeleteResponse)
