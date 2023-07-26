from typing import Tuple, List, Optional

from .common import ServiceInterface
from src.apiserver.repo import UserRepo
from ..controller.types import *
from ...components import datamodels


class AdminUserService(ServiceInterface):

    @classmethod
    async def get(cls,
                  repo: UserRepo,
                  req: UserGetRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await repo.get(username=req.username)

    @classmethod
    async def list(cls,
                   repo: UserRepo,
                   req: UserListRequest) -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:
        return await repo.list(index_start=req.index_start,
                               index_end=req.index_end,
                               extra_query_filter_str=req.extra_query_filter)

    @classmethod
    async def create(cls,
                     repo: UserRepo,
                     req: UserCreateRequest) -> Tuple[datamodels.UserModel, Optional[Exception]]:
        return await repo.create(username=req.username,
                                 password=req.password,
                                 email=req.email,
                                 role=req.role,
                                 quota=req.quota)

    @classmethod
    async def update(cls,
                     repo: UserRepo,
                     req: UserUpdateRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await repo.update(username=req.username,
                                 password=req.password,
                                 status=req.status,
                                 email=req.email,
                                 role=req.role,
                                 quota=req.quota)

    @classmethod
    async def delete(cls,
                     repo: UserRepo,
                     req: UserDeleteRequest) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        return await repo.delete(username=req.username)
