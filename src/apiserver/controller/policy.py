"""
This module implements the policy controller.
"""

import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

import src.components.auth.authn as authn
import src.components.auth.common
import src.components.errors as errors
from src.apiserver.service import RootService
from src.components.types.rbac import PolicyListRequest, PolicyListResponse, PolicyCreateRequest, \
    PolicyCreateResponse, PolicyGetRequest, PolicyGetResponse, PolicyUpdateRequest, PolicyUpdateResponse, \
    PolicyDeleteRequest, PolicyDeleteResponse
from src.components.utils.checkers import unmarshal_json_request, unmarshal_query_args
from src.components.utils.wrappers import wrapped_model_response
from src.components.auth import authn, authz


bp = Blueprint("policy", url_prefix="/policy", version=1)


@bp.get("/", name="policy_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PolicyListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
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
@authz.enforce_rbac_any(action="list", resource_fmts=["resources::/policies/*"])
async def list(request):
    """
    List all policies.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, PolicyListRequest, PolicyListResponse)
    if err is not None:
        return err_resp

    # list policies
    n, res, err = await RootService().policy_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            PolicyListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            PolicyListResponse(status=http.HTTPStatus.OK, message="success", policies=res)
        )


@bp.post("/", name="policy_create")
@openapi.definition(
    body={'application/json': PolicyCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': PolicyCreateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@authn.protected()
@authz.enforce_rbac_any(action="create", resource_fmts=["resources::/policies/*"])
async def create(request):
    """
    Create a policy.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, PolicyCreateRequest, PolicyCreateResponse)
    if err is not None:
        return err_resp

    # create policy
    res, err = await RootService().policy_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            PolicyCreateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            PolicyCreateResponse(status=http.HTTPStatus.OK, message="success", policy=res)
        )


@bp.get("/<subject_uuid:str>", name="policy_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PolicyGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@authn.protected()
@authz.enforce_rbac_any(action="read", resource_fmts=["resources::/policies/*"])
async def get(request, subject_uuid: str):
    """
    Get a policy.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check subject_uuid param in url
    if subject_uuid is None or subject_uuid == "":
        return wrapped_model_response(
            PolicyGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # get policy
        req = PolicyGetRequest(subject_uuid=subject_uuid)
        res, err = await RootService().policy_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                PolicyGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return wrapped_model_response(
                PolicyGetResponse(status=http.HTTPStatus.OK, message="success", policy=res)
            )


@bp.put("/<subject_uuid:str>", name="policy_update")
@openapi.definition(
    body={'application/json': PolicyUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': PolicyUpdateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
)
@authn.protected()
@authz.enforce_rbac_any(action="update", resource_fmts=["resources::/policies/*"])
async def update(request, subject_uuid: str):
    """
    Update a policy.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check policy param in url
    if subject_uuid is None or subject_uuid == "":
        return wrapped_model_response(
            PolicyUpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        req, err_resp, err = unmarshal_json_request(request, PolicyUpdateRequest, PolicyUpdateResponse)
        if err is not None:
            return err_resp

        req.subject_uuid = subject_uuid  # set subject_id to request

        # update policy
        _, err = await RootService().policy_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                PolicyUpdateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                PolicyUpdateResponse(status=http.HTTPStatus.OK, message="success")
            )


@bp.delete("/<subject_uuid:str>", name="policy_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PolicyDeleteResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
)
@authn.protected()
@authz.enforce_rbac_any(action="delete", resource_fmts=["resources::/policies/*"])
async def delete(request, subject_uuid: str):
    """
    Delete a policy. This will delete the policy.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check subject_uuid param in url
    if subject_uuid is None or subject_uuid == "":
        return wrapped_model_response(
            PolicyDeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # delete policy
        req = PolicyDeleteRequest(subject_uuid=subject_uuid)
        res, err = await RootService().policy_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                PolicyDeleteResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                PolicyDeleteResponse(status=http.HTTPStatus.OK, message="success")
            )


openapi.component(PolicyGetRequest)
openapi.component(PolicyGetResponse)
openapi.component(PolicyListRequest)
openapi.component(PolicyListResponse)
openapi.component(PolicyCreateRequest)
openapi.component(PolicyCreateResponse)
openapi.component(PolicyUpdateRequest)
openapi.component(PolicyUpdateResponse)
openapi.component(PolicyDeleteRequest)
openapi.component(PolicyDeleteResponse)
