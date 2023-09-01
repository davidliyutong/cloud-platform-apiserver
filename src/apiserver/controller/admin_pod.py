"""
This module implements the admin pod controller.
"""

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

bp = Blueprint("admin_pod", url_prefix="/admin/pods", version=1)


@bp.get("/", name="admin_pod_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PodListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
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
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    """
    List all pods.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    if request.query_args is None:
        req = PodListRequest()
    else:
        req = PodListRequest(**{k: v for (k, v) in request.query_args})

    # list pods
    count, pods, err = await get_root_service().pod_service.list(request.app, req)

    # return response
    if err is not None:
        return json_response(
            PodListResponse(
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(err)
            ).model_dump(),
            status=http.HTTPStatus.INTERNAL_SERVER_ERROR
        )
    else:
        return json_response(
            PodListResponse(
                status=http.HTTPStatus.OK,
                message="success",
                total_pods=count,
                pods=pods
            ).model_dump(),
            status=http.HTTPStatus.OK
        )


@bp.post("/", name="admin_pod_create")
@openapi.definition(
    body={'application/json': PodCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': PodCreateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    """
    Create a pod.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    if request.json is None:
        return json_response(
            PodCreateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        try:
            # set username to current user, this username is saved in the jwt token
            req = PodCreateRequest(**request.json)
            req.username = request.ctx.user['username'] if req.username is None else req.username
        except Exception as e:
            return json_response(
                PodCreateResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )

        # create pod
        pod, err = await get_root_service().pod_service.create(request.app, req)

        # return response
        if err is not None:
            return json_response(
                PodCreateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )

        else:
            return json_response(
                PodCreateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    pod=pod
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.get("/<pod_id:str>", name="admin_pod_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PodGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, pod_id: str):
    """
    Get a pod.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check pod_id param in url
    if pod_id is None or pod_id == "":
        return json_response(
            PodGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        # get pod
        req = PodGetRequest(pod_id=pod_id)
        pod, err = await get_root_service().pod_service.get(request.app, req)

        # return response
        if err is not None:
            return json_response(
                PodGetResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                PodGetResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    pod=pod
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.put("/<pod_id:str>", name="admin_pod_update")
@openapi.definition(
    body={'application/json': PodUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': PodUpdateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, pod_id: str):
    """
    Update a pod.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check pod_id param in url
    if pod_id is None or pod_id == "":
        return json_response(
            PodUpdateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        body = request.json
        body['force'] = True
        req = PodUpdateRequest(**body)
        req.pod_id = pod_id  # set pod_id to request

        # update pod
        pod, err = await get_root_service().pod_service.update(request.app, req)

        # return response
        if err is not None:
            return json_response(
                PodUpdateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                PodUpdateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    pod=pod
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.delete("/<pod_id:str>", name="admin_pod_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': PodDeleteResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, pod_id: str):
    """
    Delete a pod. This will mark the pod as deleted.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check pod_id param in url
    if pod_id is None or pod_id == "":
        return json_response(
            PodDeleteResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        # delete pod
        req = PodDeleteRequest(pod_id=pod_id)
        deleted_pod, err = await get_root_service().pod_service.delete(request.app, req)

        # return response
        if err is not None:
            return json_response(
                PodDeleteResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                PodDeleteResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    pod=deleted_pod
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
