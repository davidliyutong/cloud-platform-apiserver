import http
from sanic import Blueprint
from sanic.response import json as json_response
from .types import (
    UserListRequest,
    UserListResponse,
    UserCreateRequest,
    UserCreateResponse,
    UserGetRequest,
    UserGetResponse,
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteRequest,
    UserDeleteResponse
)
from sanic_ext import openapi
from sanic_jwt import protected
from loguru import logger
from src.apiserver.service import service
from src.apiserver.repo import Repo, UserRepo
import src.components.authn as authn
from ...components import errors

bp = Blueprint('admin_user', url_prefix="/admin/users", version=1)


@bp.get("/", name="admin_user_list")
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserListResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    logger.debug(f"{request.path} invoked")

    if request.query_args is None:
        req = UserListRequest()
    else:
        req = UserListRequest(**{k: v for (k, v) in request.query_args})
    repo = UserRepo(Repo(request.app.config))
    count, users, err = await service.admin_user_service.list(repo, req)

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
    body={'application/json': UserCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserCreateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    logger.debug(f"{request.path} invoked")

    if request.json is None:
        return json_response(
            UserCreateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
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
        repo = UserRepo(Repo(request.app.config))
        user, err = await service.admin_user_service.create(repo, req)

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
    pass


@bp.get("/<username:str>", name="admin_user_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserGetResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, username: str):
    logger.debug(f"{request.path} invoked")

    if username is None or username == "":
        return json_response(
            UserGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = UserGetRequest(username=username)
        repo = UserRepo(Repo(request.app.config))
        user, err = await service.admin_user_service.get(repo, req)
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
    body={'application/json': UserUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def update(request, username: str):
    logger.debug(f"{request.path} invoked")

    body = request.json
    if username is None or username == "":
        return json_response(
            UserUpdateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        body.update({"username": username})
        req = UserUpdateRequest(**body)
        repo = UserRepo(Repo(request.app.config))
        user, err = await service.admin_user_service.update(repo, req)
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
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserDeleteResponse.model_json_schema()})
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, username: str):
    logger.debug(f"{request.path} invoked")

    if username is None or username == "":
        return json_response(
            UserDeleteResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = UserDeleteRequest(username=username)
        repo = UserRepo(Repo(request.app.config))
        deleted_user, err = await service.admin_user_service.delete(repo, req)
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
