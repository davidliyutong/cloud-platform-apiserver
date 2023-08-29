"""
This module implements the admin user controller.
"""

import http

from loguru import logger
from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi
from sanic_jwt import protected

import src.components.authz as authn
from src.apiserver.service import get_root_service
from src.components import errors
from .types import *

bp = Blueprint('admin_user', url_prefix="/admin/users", version=1)


@bp.get("/", name="admin_user_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': UserListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
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
    List all users.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    if request.query_args is None:
        req = UserListRequest()
    else:
        req = UserListRequest(**{k: v for (k, v) in request.query_args})

    # list users
    count, users, err = await get_root_service().user_service.list(request.app, req)

    # return response
    if err is not None:
        return json_response(
            UserListResponse(
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(err)
            ).model_dump(),
            status=http.HTTPStatus.INTERNAL_SERVER_ERROR
        )
    else:
        return json_response(
            UserListResponse(
                status=http.HTTPStatus.OK,
                message="success",
                total_users=count,
                users=users
            ).model_dump(),
            status=http.HTTPStatus.OK
        )


@bp.post("/", name="admin_user_create")
@openapi.definition(
    body={'application/json': UserCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': UserCreateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    """
    Create a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    if request.json is None:
        return json_response(
            UserCreateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        # validate request body
        try:
            req = UserCreateRequest(**request.json)
        except Exception as e:
            return json_response(
                UserCreateResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )

        # create user
        user, err = await get_root_service().user_service.create(request.app, req)

        # return response
        if err is not None:
            return json_response(
                UserCreateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )

        else:
            return json_response(
                UserCreateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.get("/<username:str>", name="admin_user_get")
@openapi.response(
    200,
    {"application/json": UserGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")}
)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': UserGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, username: str):
    """
    Get a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check username param in url
    if username is None or username == "":
        return json_response(
            UserGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        # get user
        req = UserGetRequest(username=username)
        user, err = await get_root_service().user_service.get(request.app, req)

        # return response
        if err is not None:
            return json_response(
                UserGetResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                UserGetResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.put("/<username:str>", name="admin_user_update")
@openapi.definition(
    body={'application/json': UserUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': UserUpdateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, username: str):
    """
    Update a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check username param in url
    if username is None or username == "":
        return json_response(
            UserUpdateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        body = request.json
        req = UserUpdateRequest(**body)
        req.username = username  # set username to request
        req._skip_password_check = True  # skip password check

        # update user
        user, err = await get_root_service().user_service.update(request.app, req)

        # return response
        if err is not None:
            return json_response(
                UserUpdateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                UserUpdateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.delete("/<username:str>", name="admin_user_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': UserDeleteResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, username: str):
    """
    Delete a user. This will mark the user as deleted.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check username param in url
    if username is None or username == "":
        return json_response(
            UserDeleteResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        # check if username is the same as the current user, if so, return error
        if username == request.ctx.user['username']:
            return json_response(
                UserDeleteResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(errors.user_not_allowed)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )

        # delete user
        req = UserDeleteRequest(username=username)
        deleted_user, err = await get_root_service().user_service.delete(request.app, req)

        # return response
        if err is not None:
            return json_response(
                UserDeleteResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                UserDeleteResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=deleted_user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
