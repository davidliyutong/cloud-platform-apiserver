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
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodListResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    logger.debug(f"{request.path} invoked")

    if request.query_args is None:
        req = PodListRequest()
    else:
        req = PodListRequest(**{k: v for (k, v) in request.query_args})
    count, pods, err = await get_root_service().pod_service.list(request.app, req)

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
    body={'application/json': PodCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodCreateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    logger.debug(f"{request.path} invoked")

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
            if 'username' not in request.json.keys():
                request.json['username'] = request.ctx.user['username']
            req = PodCreateRequest(**request.json)
        except Exception as e:
            return json_response(
                PodCreateResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )
        pod, err = await get_root_service().pod_service.create(request.app, req)

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
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodGetResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, pod_id: str):
    logger.debug(f"{request.path} invoked")

    if pod_id is None or pod_id == "":
        return json_response(
            PodGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = PodGetRequest(pod_id=pod_id)
        pod, err = await get_root_service().pod_service.get(request.app, req)
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
    body={'application/json': PodUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, pod_id: str):
    logger.debug(f"{request.path} invoked")

    body = request.json
    if pod_id is None or pod_id == "":
        return json_response(
            PodUpdateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        body.update({"pod_id": pod_id})
        req = PodUpdateRequest(**body)
        pod, err = await get_root_service().pod_service.update(request.app, req)
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
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodDeleteResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, pod_id: str):
    logger.debug(f"{request.path} invoked")

    if pod_id is None or pod_id == "":
        return json_response(
            PodDeleteResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = PodDeleteRequest(pod_id=pod_id)
        deleted_pod, err = await get_root_service().pod_service.delete(request.app, req)
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
