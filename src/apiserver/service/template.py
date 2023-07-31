from typing import Tuple

from sanic import Sanic

from src.apiserver.controller.types import *
from src.apiserver.repo import TemplateRepo
from src.components import datamodels
from src.components.events import TemplateCreateEvent, TemplateUpdateEvent, TemplateDeleteEvent
from .common import ServiceInterface
from .handler import handle_template_create_event, handle_template_update_event, handle_template_delete_event


class AdminTemplateService(ServiceInterface):
    def __init__(self, template_repo: TemplateRepo):
        super().__init__()
        self.repo = template_repo

    async def get(self,
                  app: Sanic,
                  req: TemplateGetRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        return await self.repo.get(template_id=req.template_id)

    async def list(self,
                   app: Sanic,
                   req: UserListRequest) -> Tuple[int, List[datamodels.TemplateModel], Optional[Exception]]:
        return await self.repo.list(index_start=req.index_start,
                                    index_end=req.index_end,
                                    extra_query_filter_str=req.extra_query_filter)

    async def create(self,
                     app: Sanic,
                     req: TemplateCreateRequest) -> Tuple[datamodels.TemplateModel, Optional[Exception]]:
        template, err = await self.repo.create(template_name=req.template_name,
                                               description=req.description,
                                               image_ref=req.image_ref,
                                               template_str=req.template_str,
                                               fields=req.fields,
                                               defaults=req.defaults)

        if err is None:
            await app.add_task(handle_template_create_event(
                self.parent,
                TemplateCreateEvent(template_id=template.template_id))
            )

        return template, err

    async def update(self,
                     app: Sanic,
                     req: TemplateUpdateRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        template, err = await self.repo.update(template_id=req.template_id,
                                               template_name=req.template_name,
                                               description=req.description,
                                               image_ref=req.image_ref,
                                               template_str=req.template_str,
                                               fields=req.fields,
                                               defaults=req.defaults)
        if err is None:
            await app.add_task(handle_template_update_event(
                self.parent,
                TemplateUpdateEvent(template_id=template.template_id))
            )

        return template, err

    async def delete(self,
                     app: Sanic,
                     req: TemplateDeleteRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        template, err = await self.repo.delete(template_id=req.template_id)
        if err is None:
            await app.add_task(handle_template_delete_event(
                self.parent,
                TemplateDeleteEvent(template_id=template.template_id))
            )

        return template, err
