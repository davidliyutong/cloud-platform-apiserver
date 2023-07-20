import http
from abc import abstractmethod, ABCMeta
from typing import Union

from pydantic import BaseModel
from sanic import Sanic
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

app = Sanic("root")


@app.get("/health", name="health")
async def health(request):
    return json_response(
        {
            'description': '/health',
            'status': http.HTTPStatus.OK,
            'message': "OK"
        },
        http.HTTPStatus.OK
    )


class ControllerInterface(metaclass=ABCMeta):
    pass


class AuthBasicController(ControllerInterface):
    @staticmethod
    @app.post("/auth/basic", name="auth_basic", version=1)
    async def basic(request):
        pass


class AdminUserController(ControllerInterface):
    @staticmethod
    @app.get("/admin/users", name="admin_user_list", version=1)
    @openapi.definition(
        body={'application/json': AdminUserListRequest.model_json_schema()},
    )
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

    @staticmethod
    @app.post("/admin/users", name="admin_user_create", version=1)
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

    @staticmethod
    @app.get("/admin/users/<username:str>", name="admin_user_get", version=1)
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

    @staticmethod
    @app.put("/admin/users/<username:str>", name="admin_user_update", version=1)
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

    @staticmethod
    @app.delete("/admin/users/<username:str>", name="admin_user_delete", version=1)
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


class AdminTemplateController(ControllerInterface):
    @staticmethod
    @app.get("/v1/admin/templates", name="admin_template_list")
    async def list(request):
        pass

    @staticmethod
    @app.post("/v1/admin/templates", name="admin_template_create")
    async def create(request):
        pass

    @staticmethod
    @app.get("/v1/admin/templates/<templates_id:str>", name="admin_template_get")
    async def get(request, templates_id: str):
        pass

    @staticmethod
    @app.put("/v1/admin/templates/<templates_id:str>", name="admin_template_update")
    async def update(request):
        pass

    @staticmethod
    @app.delete("/v1/admin/templates/<templates_id:str>", name="admin_template_delete")
    async def delete(request):
        pass


class AdminPodController(ControllerInterface):
    @staticmethod
    @app.get("/v1/admin/pods", name="admin_pod_list")
    async def list(request):
        pass

    @staticmethod
    @app.post("/v1/admin/pods", name="admin_pod_create")
    async def create(request):
        pass

    @staticmethod
    @app.get("/v1/admin/pods/<pod_id:str>", name="admin_pod_get")
    async def get(request, pod_id: str):
        pass

    @staticmethod
    @app.put("/v1/admin/pods/<pod_id:str>", name="admin_pod_update")
    async def update(request):
        pass

    @staticmethod
    @app.delete("/v1/admin/pods/<pod_id:str>", name="admin_pod_delete")
    async def delete(request):
        pass


class NonAdminUserController(ControllerInterface):
    @staticmethod
    @app.get("/v1/user/<username>", name="user_get")
    async def get(request):
        pass

    @staticmethod
    @app.put("/v1/user/<username>", name="user_update")
    async def update(request):
        pass


class NonAdminPodController(ControllerInterface):
    @staticmethod
    @app.get("/v1/pod/<pod_id:str>", name="pod_get")
    async def get(request):
        pass

    @staticmethod
    @app.post("/v1/pod/<pod_id:str>", name="pod_create")
    async def create(request):
        pass

    @staticmethod
    @app.put("/v1/pod/<pod_id:str>", name="pod_update")
    async def update(request):
        pass

    @staticmethod
    @app.delete("/v1/pod/<pod_id:str>", name="pod_delete")
    async def delete(request):
        pass


@app.main_process_start
async def main_process_start(application):
    logger = create_logger()
    logger.info("main process start")
