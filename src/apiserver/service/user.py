import json
from typing import Tuple

from loguru import logger
from sanic import Sanic

from src.apiserver.controller.types import *
from src.apiserver.repo import UserRepo
from src.components import datamodels, errors
from src.components.events import UserCreateEvent, UserUpdateEvent, UserDeleteEvent
from .common import ServiceInterface
from .handler import handle_user_create_event, handle_user_update_event, handle_user_delete_event


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
        if req.extra_query_filter != "":
            try:
                query_filter = json.loads(req.extra_query_filter)
            except json.JSONDecodeError:
                logger.error(f"extra_query_filter_str is not a valid json string: {req.extra_query_filter}")
                return 0, [], errors.wrong_query_filter
        else:
            query_filter = {}
        return await self.repo.list(index_start=req.index_start,
                                    index_end=req.index_end,
                                    extra_query_filter=query_filter)

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
