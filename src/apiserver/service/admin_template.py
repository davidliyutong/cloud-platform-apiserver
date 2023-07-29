from typing import Tuple
from .common import ServiceInterface
from src.apiserver.repo import TemplateRepo
from src.apiserver.controller.types import *
from src.components import datamodels


class AdminTemplateService(ServiceInterface):
    def __init__(self, template_repo: TemplateRepo):
        super().__init__()
        self.repo = template_repo

    async def get(self,
                  req: TemplateGetRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        return await self.repo.get(template_id=req.template_id)

    async def list(self,
                   req: UserListRequest) -> Tuple[int, List[datamodels.TemplateModel], Optional[Exception]]:
        return await self.repo.list(index_start=req.index_start,
                                    index_end=req.index_end,
                                    extra_query_filter_str=req.extra_query_filter)

    async def create(self,
                     req: TemplateCreateRequest) -> Tuple[datamodels.TemplateModel, Optional[Exception]]:
        return await self.repo.create(template_name=req.template_name,
                                      description=req.description,
                                      image_ref=req.image_ref,
                                      template_str=req.template_str,
                                      fields=req.fields,
                                      defaults=req.defaults)

    async def update(self,
                     req: TemplateUpdateRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        return await self.repo.update(template_id=req.template_id,
                                      template_name=req.template_name,
                                      description=req.description,
                                      image_ref=req.image_ref,
                                      template_str=req.template_str,
                                      fields=req.fields,
                                      defaults=req.defaults)

    async def delete(self,
                     req: TemplateDeleteRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        return await self.repo.delete(template_id=req.template_id)
