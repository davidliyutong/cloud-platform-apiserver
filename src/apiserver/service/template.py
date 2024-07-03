# FILE A
"""
Template service
"""

from typing import Tuple, Optional, List, Type, Union

from odmantic import AIOEngine
from sanic import Sanic

from src.components import errors
from src.components.datamodels import TemplateModelV2, ResourceStatusEnum
from src.components.types.template import (
    TemplateListRequest,
    TemplateCreateRequest,
    TemplateGetRequest,
    TemplateUpdateRequest,
    TemplateDeleteRequest
)
from src.components.utils.checkers import unmarshal_mongodb_filter
from .common import ServiceInterface


class TemplateService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self._engine = odm_engine

    async def get(self, app: Sanic, req: TemplateGetRequest) -> Tuple[Optional[TemplateModelV2], Optional[Exception]]:
        """
        Get template.
        """
        res = await self._engine.find_one(TemplateModelV2, TemplateModelV2.template_uuid == req.template_uuid)
        return res, None if res is not None else Exception(errors.template_not_found)

    async def list(
            self, app: Sanic, req: Union[TemplateListRequest, Type[TemplateListRequest]]
    ) -> Tuple[int, List[TemplateModelV2], Optional[Exception]]:
        """
        List templates.
        """
        query_filter, err = unmarshal_mongodb_filter(req.extra_query_filter)

        if err is not None:
            return 0, [], err

        res = await self._engine.find(TemplateModelV2, query_filter, skip=req.skip, limit=req.limit)
        count = await self._engine.count(TemplateModelV2, query_filter)

        return count, res, None

    async def create(
            self, app: Sanic, req: Union[TemplateCreateRequest, Type[TemplateCreateRequest]]
    ) -> Tuple[Optional[TemplateModelV2], Optional[Exception]]:
        """
        Create a template.
        """
        try:
            template = TemplateModelV2(**req.dict())
            if not template.verify():
                return None, Exception(errors.template_invalid)
            await self._engine.save(template)
        except Exception as e:
            return None, e

        return template, None

    async def update(
            self, app: Sanic, req: Union[TemplateUpdateRequest, Type[TemplateUpdateRequest]]
    ) -> Tuple[Optional[TemplateModelV2], Optional[Exception]]:
        """
        Update a template.
        """
        template = await self._engine.find_one(
            TemplateModelV2, TemplateModelV2.template_uuid == req.template_uuid
        )

        if template is None:
            return None, Exception(errors.template_not_found)

        # selectively update fields
        template.name = req.name if req.name is not None else template.name
        template.description = req.description if req.description is not None else template.description

        template.template_type = req.template_type if req.template_type is not None else template.template_type
        template.image_ref = req.image_ref if req.image_ref is not None else template.image_ref
        template.template_str = req.template_str if req.template_str is not None else template.template_str

        if not template.verify():
            return None, Exception(errors.template_invalid)

        template.resource_status = ResourceStatusEnum.committed
        try:
            await self._engine.save(template)
        except Exception as e:
            return None, e

        return template, None

    async def delete(
            self, app: Sanic, req: Union[TemplateDeleteRequest, Type[TemplateDeleteRequest]]
    ) -> Tuple[Optional[TemplateModelV2], Optional[Exception]]:
        """
        Delete a template.
        """
        template = await self._engine.find_one(
            TemplateModelV2, TemplateModelV2.template_uuid == req.template_uuid
        )

        if template is None:
            return None, Exception(errors.template_not_found)

        try:
            await self._engine.delete(template)
        except Exception as e:
            return None, e

        return template, None
