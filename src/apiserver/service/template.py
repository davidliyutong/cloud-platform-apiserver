"""
Template service
"""

import json
from typing import Tuple

from loguru import logger
from sanic import Sanic

from src.apiserver.controller.types import *
from src.apiserver.repo import TemplateRepo
from src.components import datamodels, errors
from src.components.events import TemplateCreateEvent, TemplateUpdateEvent, TemplateDeleteEvent
from .common import ServiceInterface
from .handler import handle_template_create_event, handle_template_update_event, handle_template_delete_event


class TemplateService(ServiceInterface):
    def __init__(self, template_repo: TemplateRepo):
        super().__init__()
        self.repo: TemplateRepo = template_repo

    async def get(self,
                  app: Sanic,
                  req: TemplateGetRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Get template.
        """
        return await self.repo.get(template_id=req.template_id)

    async def list(self,
                   app: Sanic,
                   req: UserListRequest) -> Tuple[int, List[datamodels.TemplateModel], Optional[Exception]]:
        """
        List templates.
        """

        # build query filter from json string
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
                     req: TemplateCreateRequest) -> Tuple[datamodels.TemplateModel, Optional[Exception]]:
        """
        Create a template.
        """

        template, err = await self.repo.create(name=req.name,
                                               description=req.description,
                                               image_ref=req.image_ref,
                                               template_str=req.template_str,
                                               fields=req.fields,
                                               defaults=req.defaults)

        # if success, trigger template create event
        if err is None:
            await app.add_task(handle_template_create_event(
                self.parent,
                TemplateCreateEvent(template_id=str(template.template_id)))
            )

        return template, err

    async def update(self,
                     app: Sanic,
                     req: TemplateUpdateRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Update a template.
        """

        template, err = await self.repo.update(template_id=req.template_id,
                                               name=req.name,
                                               description=req.description,
                                               image_ref=req.image_ref,
                                               template_str=req.template_str,
                                               fields=req.fields,
                                               defaults=req.defaults)

        # if success and target_status is pending, trigger template update event
        if err is None and template.resource_status == datamodels.ResourceStatusEnum.pending:
            await app.add_task(handle_template_update_event(
                self.parent,
                TemplateUpdateEvent(template_id=str(template.template_id)))
            )

        return template, err

    async def delete(self,
                     app: Sanic,
                     req: TemplateDeleteRequest) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Delete a template.
        """

        template, err = await self.repo.delete(template_id=req.template_id)

        # if success, trigger template delete event
        if err is None:
            await app.add_task(handle_template_delete_event(
                self.parent,
                TemplateDeleteEvent(template_id=str(template.template_id)))
            )

        return template, err
