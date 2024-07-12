# FILE A
"""
Template service
"""

from typing import Tuple, Optional, List, Type, Union

from odmantic import AIOEngine
from sanic import Sanic

from src.components import errors
from src.components.datamodels.template import (
    PodTemplateModelV2, ResourceStatusEnum, VolumeTemplateModelV2,
)

from src.components.types.template import (
    PodTemplateListRequest,
    PodTemplateCreateRequest,
    PodTemplateGetRequest,
    PodTemplateUpdateRequest,
    PodTemplateDeleteRequest
)

from src.components.types.template import (
    VolumeTemplateListRequest,
    VolumeTemplateCreateRequest,
    VolumeTemplateGetRequest,
    VolumeTemplateUpdateRequest,
    VolumeTemplateDeleteRequest
)
from src.components.utils.checkers import unmarshal_mongodb_filter
from .common import ServiceInterface


class PodTemplateService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self._engine = odm_engine

    async def get(self, app: Sanic, req: PodTemplateGetRequest) -> Tuple[
        Optional[PodTemplateModelV2], Optional[Exception]]:
        """
        Get pod template.
        """
        res = await self._engine.find_one(PodTemplateModelV2, PodTemplateModelV2.template_uuid == req.template_uuid)
        return res, None if res is not None else Exception(errors.template_not_found)

    async def list(
            self, app: Sanic, req: Union[PodTemplateListRequest, Type[PodTemplateListRequest]],
            public_only: bool = False
    ) -> Tuple[int, List[PodTemplateModelV2], Optional[Exception]]:
        """
        List pod templates.
        """
        query_filter, err = unmarshal_mongodb_filter(req.extra_query_filter)

        if public_only:
            query_filter = {"$and": [query_filter, {"public": True}]}

        if err is not None:
            return 0, [], err

        res = await self._engine.find(PodTemplateModelV2, query_filter, skip=req.skip, limit=req.limit)
        count = await self._engine.count(PodTemplateModelV2, query_filter)

        return count, res, None

    async def create(
            self, app: Sanic, req: Union[PodTemplateCreateRequest, Type[PodTemplateCreateRequest]]
    ) -> Tuple[Optional[PodTemplateModelV2], Optional[Exception]]:
        """
        Create a pod template.
        """
        try:
            template = PodTemplateModelV2(**req.dict())
            if not template.verify():
                return None, Exception(errors.template_invalid)
            await self._engine.save(template)
        except Exception as e:
            return None, e

        return template, None

    async def update(
            self, app: Sanic, req: Union[PodTemplateUpdateRequest, Type[PodTemplateUpdateRequest]]
    ) -> Tuple[Optional[PodTemplateModelV2], Optional[Exception]]:
        """
        Update a pod template.
        """
        template = await self._engine.find_one(
            PodTemplateModelV2, PodTemplateModelV2.template_uuid == req.template_uuid
        )

        if template is None:
            return None, Exception(errors.template_not_found)

        # selectively update fields
        template.name = req.name if req.name is not None else template.name
        template.description = req.description if req.description is not None else template.description
        template.public = req.public if req.public is not None else template.public

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
            self, app: Sanic, req: Union[PodTemplateDeleteRequest, Type[PodTemplateDeleteRequest]]
    ) -> Tuple[Optional[PodTemplateModelV2], Optional[Exception]]:
        """
        Delete a pod template.
        """
        template = await self._engine.find_one(
            PodTemplateModelV2, PodTemplateModelV2.template_uuid == req.template_uuid
        )

        if template is None:
            return None, Exception(errors.template_not_found)

        try:
            await self._engine.delete(template)
        except Exception as e:
            return None, e

        return template, None


class VolumeTemplateService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self._engine = odm_engine

    async def get(self, app: Sanic, req: VolumeTemplateGetRequest) -> Tuple[
        Optional[VolumeTemplateModelV2], Optional[Exception]]:
        """
        Get volume template.
        """
        res = await self._engine.find_one(VolumeTemplateModelV2,
                                          VolumeTemplateModelV2.template_uuid == req.template_uuid)
        return res, None if res is not None else Exception(errors.template_not_found)

    async def list(
            self, app: Sanic, req: Union[VolumeTemplateListRequest, Type[VolumeTemplateListRequest]],
            public_only: bool = False
    ) -> Tuple[int, List[VolumeTemplateModelV2], Optional[Exception]]:
        """
        List volume templates.
        """
        query_filter, err = unmarshal_mongodb_filter(req.extra_query_filter)

        if err is not None:
            return 0, [], err

        if public_only:
            query_filter = {"$and": [query_filter, {"public": True}]}

        res = await self._engine.find(VolumeTemplateModelV2, query_filter, skip=req.skip, limit=req.limit)
        count = await self._engine.count(VolumeTemplateModelV2, query_filter)

        return count, res, None

    async def create(
            self, app: Sanic, req: Union[VolumeTemplateCreateRequest, Type[VolumeTemplateCreateRequest]]
    ) -> Tuple[Optional[VolumeTemplateModelV2], Optional[Exception]]:
        """
        Create a volume template.
        """
        try:
            template = VolumeTemplateModelV2(**req.dict())
            if not template.verify():
                return None, Exception(errors.template_invalid)
            await self._engine.save(template)
        except Exception as e:
            return None, e

        return template, None

    async def update(
            self, app: Sanic, req: Union[VolumeTemplateUpdateRequest, Type[VolumeTemplateUpdateRequest]]
    ) -> Tuple[Optional[VolumeTemplateModelV2], Optional[Exception]]:
        """
        Update a volume template.
        """
        template = await self._engine.find_one(
            VolumeTemplateModelV2, VolumeTemplateModelV2.template_uuid == req.template_uuid
        )

        if template is None:
            return None, Exception(errors.template_not_found)

        # selectively update fields
        template.name = req.name if req.name is not None else template.name
        template.description = req.description if req.description is not None else template.description
        template.public = req.public if req.public is not None else template.public

        template.template_type = req.template_type if req.template_type is not None else template.template_type
        template.storage_class = req.storage_class if req.storage_class is not None else template.storage_class
        template.max_size_mb = req.max_size_mb if req.max_size_mb is not None else template.max_size_mb
        template.mount_type = req.mount_type if req.mount_type is not None else template.mount_type
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
            self, app: Sanic, req: Union[VolumeTemplateDeleteRequest, Type[VolumeTemplateDeleteRequest]]
    ) -> Tuple[Optional[VolumeTemplateModelV2], Optional[Exception]]:
        """
        Delete a volume template.
        """
        template = await self._engine.find_one(
            VolumeTemplateModelV2, VolumeTemplateModelV2.template_uuid == req.template_uuid
        )

        if template is None:
            return None, Exception(errors.template_not_found)

        try:
            await self._engine.delete(template)
        except Exception as e:
            return None, e

        return template, None
