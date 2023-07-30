from typing import Tuple

from .common import ServiceInterface
from src.apiserver.repo import UserRepo
from src.apiserver.controller.types import *
from src.components import datamodels


class AdminUserService(ServiceInterface):

    def __init__(self, user_repo: UserRepo):
        super().__init__()
        self.repo = user_repo

    async def get(self,
                  req: UserGetRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await self.repo.get(username=req.username)

    async def list(self,
                   req: UserListRequest) -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:
        return await self.repo.list(index_start=req.index_start,
                                    index_end=req.index_end,
                                    extra_query_filter_str=req.extra_query_filter)

    async def create(self,
                     req: UserCreateRequest) -> Tuple[datamodels.UserModel, Optional[Exception]]:
        return await self.repo.create(username=req.username,
                                      password=req.password,
                                      email=req.email,
                                      role=req.role,
                                      quota=req.quota)

    async def update(self,
                     req: UserUpdateRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await self.repo.update(username=req.username,
                                      password=req.password,
                                      status=req.status,
                                      email=req.email,
                                      role=req.role,
                                      quota=req.quota)

    async def delete(self,
                     req: UserDeleteRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await self.repo.delete(username=req.username)
