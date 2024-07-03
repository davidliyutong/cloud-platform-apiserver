"""
This module implements the admin user controller.
"""

import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi
# from sanic_jwt import protected

from src.components import errors
from src.apiserver.service import RootService
from src.components.types import *
from src.components.utils.wrappers import wrapped_model_response
from src.components.utils.checkers import unmarshal_query_args, unmarshal_json_request

from src.components.auth import authn, authz

bp = Blueprint('user', url_prefix="/users", version=1)


@bp.get("/", name="admin_user_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': UserListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200
        )
    ],
    parameter=[
        openapi.definitions.Parameter("index_start", int, location="query", required=False),
        openapi.definitions.Parameter("index_end", int, location="query", required=False),
        openapi.definitions.Parameter("extra_query_filter", str, location="query", required=False)
    ],
    secured={"token": []}
)
@authn.protected()
@authz.enforce_rbac_any(action="list", resource_fmts=["resources::/users/*"])
async def list(request):
    """
    List all users.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, UserListRequest, UserListResponse)
    if err is not None:
        return err_resp

    # list users
    count, users, err = await RootService().user_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            UserListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            UserListResponse(status=http.HTTPStatus.OK, message="success", total_users=count, users=users)
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
@authn.protected()
@authz.enforce_rbac_any(action="create", resource_fmts=["resources::/users/*"])
async def create(request):
    """
    Create a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, UserCreateRequest, UserCreateResponse)
    if req.group is None:
        req.group = GroupEnumInternal.default

    if err is not None:
        return err_resp

    # create user
    user, err = await RootService().user_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            UserCreateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )

    else:
        return wrapped_model_response(
            UserCreateResponse(status=http.HTTPStatus.OK, message="success", user=user)
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
@authn.protected()
@authz.enforce_rbac_any(action="read", resource_fmts=["resources::/users/{username}"])
async def get(request, username: str):
    """
    Get a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check username param in url
    if username is None or username == "":
        return wrapped_model_response(
            UserGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # get user
        req = UserGetRequest(username=username)

        user, err = await RootService().user_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                UserGetResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                UserGetResponse(status=http.HTTPStatus.OK, message="success", user=user)
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
@authn.protected()
@authz.enforce_rbac_any(action="update", resource_fmts=["resources::/users/{username}"])
async def update(request, username: str):
    """
    Update a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check username param in url
    if username is None or username == "":
        return wrapped_model_response(
            UserUpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        req, err_resp, err = unmarshal_json_request(request, UserUpdateRequest, UserUpdateResponse)
        if err is not None:
            return err_resp

        req.username = username  # set username to request

        # conditional check if user is allowed to update by force
        if any([
            req.update_password and req.old_password is None,
            req.update_quota,
            req.update_group,
            req.update_status
        ]):
            result = await RootService().policy_service.enforce(
                request.app,
                request.ctx.rbac_id, 'update', "resources::/users/*"
            )
            if not result:
                return wrapped_model_response(
                    UserUpdateResponse(status=http.HTTPStatus.UNAUTHORIZED, message=str(errors.user_not_allowed))
                )

        # update user
        # FIXME
        user, err = await RootService().user_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                UserUpdateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                UserUpdateResponse(status=http.HTTPStatus.OK, message="success", user=user)
            )


@bp.delete("/<username:str>", name="admin_user_delete")
@openapi.definition(
    body={'application/json': UserDeleteRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': UserDeleteResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={"token": []}
)
@authn.protected()
@authz.enforce_rbac_any(action="delete", resource_fmts=["resources::/users/{username}"])
async def delete(request, username: str):
    """
    Delete a user.
    """
    # note: This will mark the user as deleted.

    logger.debug(f"{request.method} {request.path} invoked")

    # check username param in url
    if username is None or username == "":
        return wrapped_model_response(
            UserDeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # delete user
        req, err_resp, err = unmarshal_json_request(request, UserDeleteRequest, UserDeleteResponse)
        if err is not None:
            return err_resp
        req.username = username  # set username to request

        # conditional check if user is allowed to delete by force
        if any([
            req.password is None,
        ]):
            result = await RootService().policy_service.enforce(
                request.app,
                request.ctx.rbac_id, 'delete', "resources::/users/*"
            )
            if not result:
                return wrapped_model_response(
                    UserUpdateResponse(status=http.HTTPStatus.UNAUTHORIZED, message=str(errors.user_not_allowed))
                )

        deleted_user, err = await RootService().user_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                UserDeleteResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                UserDeleteResponse(status=http.HTTPStatus.OK, message="success", user=deleted_user)
            )


openapi.component(UserListRequest)
openapi.component(UserListResponse)
openapi.component(UserCreateRequest)
openapi.component(UserCreateResponse)
openapi.component(UserGetRequest)
openapi.component(UserGetResponse)
openapi.component(UserUpdateRequest)
openapi.component(UserUpdateResponse)
openapi.component(UserDeleteRequest)
openapi.component(UserDeleteResponse)
