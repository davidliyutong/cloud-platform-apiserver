import http
from abc import abstractmethod, ABCMeta
from typing import Union

from pydantic import BaseModel
from sanic import Sanic, Blueprint
from sanic.response import json as json_response
from .types import *
from sanic_ext import validate, openapi
from sanic_jwt import protected
from loguru import logger
from src.apiserver.service import service
from src.apiserver.repo import Repo, UserRepo
from src.components.config import BackendConfig
from src.components.logging import create_logger
import src.components.authn as authn
from ...components import errors

bp = Blueprint('admin_user', url_prefix="/admin/users", version=1)


@bp.get("/", name="admin_user_list")
@openapi.parameter("index_start", int, location="query", required=False)
@openapi.parameter("index_end", int, location="query", required=False)
@openapi.parameter("extra_query_filter", str, location="query", required=False)
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def list(request):
    logger.debug(f"{request.path} invoked")

    if request.query_args is None:
        req = AdminUserListRequest()
    else:
        req = AdminUserListRequest(**{k: v for (k, v) in request.query_args})
    repo = UserRepo(Repo(request.app.config))
    count, users, err = await service.admin_user_service.list(repo, req)

    if err is not None:
        return json_response(
            AdminUserListResponse(
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(err)
            ).model_dump(),
            status=http.HTTPStatus.INTERNAL_SERVER_ERROR
        )
    else:
        return json_response(
            AdminUserListResponse(
                status=http.HTTPStatus.OK,
                message="success",
                total_users=count,
                users=users
            ).model_dump(),
            status=http.HTTPStatus.OK
        )


@bp.post("/", name="admin_user_create")
@openapi.definition(
    body={'application/json': AdminUserCreateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def create(request):
    logger.debug(f"{request.path} invoked")

    if request.json is None:
        return json_response(
            AdminUserCreateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        try:
            req = AdminUserCreateRequest(**request.json)
        except Exception as e:
            return json_response(
                AdminUserCreateResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ).model_dump(),
                status=http.HTTPStatus.BAD_REQUEST
            )
        repo = UserRepo(Repo(request.app.config))
        user, err = await service.admin_user_service.create(repo, req)

        if err is not None:
            return json_response(
                AdminUserCreateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )

        else:
            return json_response(
                AdminUserCreateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
    pass


@bp.get("/<username:str>", name="admin_user_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def get(request, username: str):
    logger.debug(f"{request.path} invoked")

    if username is None or username == "":
        return json_response(
            AdminUserGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = AdminUserGetRequest(username=username)
        repo = UserRepo(Repo(request.app.config))
        user, err = await service.admin_user_service.get(repo, req)
        if err is not None:
            return json_response(
                AdminUserGetResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                AdminUserGetResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.put("/<username:str>", name="admin_user_update")
@openapi.definition(
    body={'application/json': AdminUserUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@authn.validate_role(role=("admin", "super_admin"))
@protected()
async def update(request, username: str):
    logger.debug(f"{request.path} invoked")

    body = request.json
    if username is None or username == "":
        return json_response(
            AdminUserGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        body.update({"username": username})
        req = AdminUserUpdateRequest(**body)
        repo = UserRepo(Repo(request.app.config))
        user, err = await service.admin_user_service.update(repo, req)
        if err is not None:
            return json_response(
                AdminUserUpdateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                AdminUserGetResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.delete("/<username:str>", name="admin_user_delete")
@openapi.parameter("Authorization", str, location="header", required=True)
@protected()
@authn.validate_role(role=("admin", "super_admin"))
async def delete(request, username: str):
    logger.debug(f"{request.path} invoked")

    if username is None or username == "":
        return json_response(
            AdminUserGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        req = AdminUserDeleteRequest(username=username)
        repo = UserRepo(Repo(request.app.config))
        deleted_user, err = await service.admin_user_service.delete(repo, req)
        if err is not None:
            return json_response(
                AdminUserDeleteResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                AdminUserDeleteResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=deleted_user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
