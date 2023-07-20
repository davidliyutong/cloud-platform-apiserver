from typing import Tuple, List, Optional

from .common import ServiceInterface
from src.apiserver.repo import UserRepo
from ..controller.types import AdminUserListRequest
from ...components import datamodels


class AdminUserService(ServiceInterface):
    @classmethod
    async def list(cls,
                   repo: UserRepo,
                   req: AdminUserListRequest) -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:
        return await repo.list(uid_start=req.uid_start,
                               uid_end=req.uid_end,
                               extra_query_filter_str=req.extra_query_filter)
