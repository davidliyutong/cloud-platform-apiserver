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

app = Sanic("root")


class ControllerInterface(metaclass=ABCMeta):
    pass


# class AuthJWTController(ControllerInterface):
#     @staticmethod
#     @app.post("/auth/jwt/login", name="auth_jwt_login", version=1)
#     @openapi.definition(
#         body={'application/json': AuthJWTLoginRequest.model_json_schema()},
#     )
#     @validate(json=AuthJWTLoginRequest)
#     async def jwt_login(request, body: AuthJWTLoginRequest):
#         logger.debug(f"login request: {body}")
#         repo = Repo(request.app.config)
#         token, expire, err = await service.auth_jwt_service.login(repo, body.username, body.password)
#         if err is not None:
#             return json_response(
#                 AuthJWTLoginResponse(code="ok", expire=datetime.datetime.now(), token=token).model_dump(), status=500)
#         else:
#             return json_response(AuthJWTLoginResponse(code="ok", expire=expire, token=token).model_dump(), status=500)
#
#     @staticmethod
#     @app.post("/auth/jwt/refresh", name="auth_jwt_refresh", version=1)
#     async def jwt_refresh(request):
#         pass


class AuthBasicController(ControllerInterface):
    @staticmethod
    @app.post("/auth/basic", name="auth_basic", version=1)
    async def basic(request):
        pass


class AdminUserController(ControllerInterface):
    @staticmethod
    @app.get("/admin/users", name="admin_user_list", version=1)
    # @protected()
    @openapi.definition(
        body={'application/json': AdminUserListRequest.model_json_schema()},
    )
    async def list(request):
        req = request.json
        if req is None:
            req = AdminUserListRequest()
        else:
            req = AdminUserListRequest(**req)
        repo = UserRepo(Repo(request.app.config))
        count, users, err = await service.admin_user_service.list(repo, req)

        if err is not None:
            return json_response(AdminUserListResponse(code=500, msg=str(err)).model_dump(),
                                 status=http.HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            return json_response(
                AdminUserListResponse(
                    code=200,
                    msg=str(err),
                    total_users=count,
                    users=users
                ).model_dump(), status=http.HTTPStatus.OK)

    @staticmethod
    @app.post("/admin/users", name="admin_user_create", version=1)
    async def create(request):
        pass

    @staticmethod
    @app.get("/admin/users/<user_id:str>", name="admin_user_get", version=1)
    async def get(request, user_id: str):
        pass

    @staticmethod
    @app.put("/admin/users/<user_id:str>", name="admin_user_update", version=1)
    async def update(request, user_id: str):
        pass

    @staticmethod
    @app.delete("/admin/users/<user_id:str>", name="admin_user_delete", version=1)
    async def delete(request, user_id: str):
        pass


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
