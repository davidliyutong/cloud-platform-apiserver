import base64
from typing import Union
from typing import Tuple

import kubernetes
from kubernetes.client import ApiException
from loguru import logger
from sanic import Sanic

from src.apiserver.controller.types import *
from src.apiserver.repo import UserRepo
from src.components import config
from src.components import datamodels
from src.components.events import UserCreateEvent, UserUpdateEvent, UserDeleteEvent
from .common import ServiceInterface
import src.apiserver.service


async def handle_user_create_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserCreateEvent, BaseModel]) -> Optional[Exception]:
    user, err = await srv.admin_user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"creating k8s credentials for user {ev.username}")
        err = None
        try:
            ret = srv.k8s_operator_service.v1.create_namespaced_secret(
                config.CONFIG_PROJECT_NAMESPACE,
                kubernetes.client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    data={
                        "auth": base64.b64encode(user.htpasswd.get_secret_value().encode()).decode()
                    },
                    metadata=kubernetes.client.V1ObjectMeta(
                        name=f"{user.username}-basic-auth",
                        namespace=config.CONFIG_PROJECT_NAMESPACE
                    )
                ))
            if ret is None:
                err = RuntimeError("failed to create k8s secret")
        except ApiException as e:
            if e.reason == 'Conflict':
                logger.warning(f"secret {user.username}-basic-auth already exists")
            else:
                logger.error(e)
                err = e
        if err is None:
            return RuntimeError("failed to create k8s secret")
        else:
            err = await srv.admin_user_service.repo.commit(ev.username)
            if err is not None:
                logger.error(f"handle_user_create_event failed to commit: {err}")
                return err
            else:
                return err
    return None


async def handle_user_update_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserUpdateEvent, BaseModel]) -> Optional[Exception]:
    user, err = await srv.admin_user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"updating k8s credentials for user {ev.username}")
        err = None
        try:
            ret = srv.k8s_operator_service.v1.patch_namespaced_secret(
                f"{user.username}-basic-auth",
                config.CONFIG_PROJECT_NAMESPACE,
                kubernetes.client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    data={
                        "auth": base64.b64encode(user.htpasswd.get_secret_value().encode()).decode()
                    },
                    metadata=kubernetes.client.V1ObjectMeta(
                        name=f"{user.username}-basic-auth",
                        namespace=config.CONFIG_PROJECT_NAMESPACE
                    )
                ))
            if ret is None:
                err = RuntimeError("failed to update k8s secret")
        except ApiException as e:
            if e.reason == 'Not Found':
                logger.warning(f"secret {user.username}-basic-auth not found")
            else:
                logger.error(e)
                err = e
        if err is None:
            return RuntimeError("failed to update k8s secret")
        else:
            err = await srv.admin_user_service.repo.commit(ev.username)
            if err is not None:
                logger.error(f"handle_user_update_event failed to commit: {err}")
                return err
            else:
                return err
    return None


async def handle_user_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserDeleteEvent, BaseModel]) -> Optional[Exception]:
    user, err = await srv.admin_user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"deleting k8s credentials for user {ev.username}")
        err = None
        try:
            ret = srv.k8s_operator_service.v1.delete_namespaced_secret(
                f"{user.username}-basic-auth",
                config.CONFIG_PROJECT_NAMESPACE,
            )
            if ret is None:
                err = RuntimeError("failed to delete k8s secret")
        except ApiException as e:
            if e.reason == 'Not Found':
                logger.warning(f"secret {user.username}-basic-auth not found")
            else:
                logger.error(e)
                err = e

        if err is not None:
            return err
        else:
            _, err = await srv.admin_user_service.repo.purge(ev.username)
            if err is not None:
                logger.error(f"handle_user_delete_event failed to commit: {err}")
                return err
            else:
                return err


class AdminUserService(ServiceInterface):

    def __init__(self, user_repo: UserRepo):
        super().__init__()
        self.repo = user_repo

    async def get(self,
                  app: Sanic,
                  req: UserGetRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await self.repo.get(username=req.username)

    async def list(self,
                   app: Sanic,
                   req: UserListRequest) -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:
        return await self.repo.list(index_start=req.index_start,
                                    index_end=req.index_end,
                                    extra_query_filter_str=req.extra_query_filter)

    async def create(self,
                     app: Sanic,
                     req: UserCreateRequest) -> Tuple[datamodels.UserModel, Optional[Exception]]:
        user, err = await self.repo.create(username=req.username,
                                           password=req.password,
                                           email=req.email,
                                           role=req.role,
                                           quota=req.quota)
        if err is None:
            await app.add_task(handle_user_create_event(self.parent, UserCreateEvent(username=user.username)))
        return user, err

    async def update(self,
                     app: Sanic,
                     req: UserUpdateRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        user, err = await self.repo.update(username=req.username,
                                           password=req.password,
                                           status=req.status,
                                           email=req.email,
                                           role=req.role,
                                           quota=req.quota)

        if err is None:
            await app.add_task(handle_user_update_event(self.parent, UserUpdateEvent(username=user.username)))

        return user, err

    async def delete(self,
                     app: Sanic,
                     req: UserDeleteRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        user, err = await self.repo.delete(username=req.username)

        if err is None:
            await app.add_task(handle_user_delete_event(self.parent, UserDeleteEvent(username=user.username)))

        return user, err
