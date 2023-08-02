import http

from loguru import logger
from sanic import Blueprint
from sanic.response import json as json_response
from sanic.response import text
from sanic_ext import openapi
from sanic_jwt import protected

import src.components.authz as authn
import src.components.errors as errors
from src.apiserver.service import get_root_service
from .types import *

bp = Blueprint("nonadmin_pod", url_prefix="/pods", version=1)


@bp.get("/", name="nonadmin_pod_list")
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodListResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def list(request):
    logger.debug(f"{request.method} {request.path} invoked")

    if request.query_args is None:
        req = PodListRequest()
    else:
        req = PodListRequest(**{k: v for (k, v) in request.query_args})

    count, pods, err = await get_root_service().pod_service.list(request.app, req)
    pods = [p for p in pods if p.username == request.ctx.user['username']]
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


@bp.post("/", name="nonadmin_pod_create")
@openapi.definition(
    body={'application/json': PodCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodCreateResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def create(request):
    logger.debug(f"{request.method} {request.path} invoked")

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
            request.json['uid'] = request.ctx.user['uid']
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


@bp.get("/<pod_id:str>", name="nonadmin_pod_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodGetResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def get(request, pod_id: str):
    logger.debug(f"{request.method} {request.path} invoked")

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
        if pod.username != request.ctx.user['username']:
            return json_response(
                PodGetResponse(
                    status=http.HTTPStatus.UNAUTHORIZED,
                    message="cannot get pods that does not belong to current user"
                ).model_dump(),
                status=http.HTTPStatus.UNAUTHORIZED
            )

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


@bp.put("/<pod_id:str>", name="nonadmin_pod_update")
@openapi.definition(
    body={'application/json': PodUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def update(request, pod_id: str):
    logger.debug(f"{request.method} {request.path} invoked")

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
        req = PodGetRequest(**body)
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
            if pod.username != request.ctx.user['username']:
                return json_response(
                    PodGetResponse(
                        status=http.HTTPStatus.UNAUTHORIZED,
                        message="cannot update pods that does not belong to current user"
                    ).model_dump(),
                    status=http.HTTPStatus.UNAUTHORIZED
                )

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


@bp.delete("/<pod_id:str>", name="nonadmin_pod_delete")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": PodDeleteResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def delete(request, pod_id: str):
    logger.debug(f"{request.method} {request.path} invoked")

    if pod_id is None or pod_id == "":
        return json_response(
            PodDeleteResponse(
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
            if pod.username != request.ctx.user['username']:
                return json_response(
                    PodGetResponse(
                        status=http.HTTPStatus.UNAUTHORIZED,
                        message="cannot update pods that does not belong to current user"
                    ).model_dump(),
                    status=http.HTTPStatus.UNAUTHORIZED
                )

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
