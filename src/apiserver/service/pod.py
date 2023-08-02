"""
Pod service
"""

import json
from typing import Tuple

from loguru import logger
from sanic import Sanic

from src.apiserver.controller.types import *
from src.apiserver.repo import PodRepo
from src.components import datamodels, errors
from src.components.events import PodCreateUpdateEvent, PodDeleteEvent
from .common import ServiceInterface
from .handler import handle_pod_create_update_event, handle_pod_delete_event


class PodService(ServiceInterface):
    def __init__(self, pod_repo: PodRepo):
        super().__init__()
        self.repo = pod_repo

    async def get(self,
                  app: Sanic,
                  req: PodGetRequest) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Get pod.
        """

        return await self.repo.get(pod_id=req.pod_id)

    async def list(self,
                   app: Sanic,
                   req: PodListRequest) -> Tuple[int, List[datamodels.PodModel], Optional[Exception]]:
        """
        List pods.
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
                     req: PodCreateRequest) -> Tuple[datamodels.PodModel, Optional[Exception]]:
        """
        Create a pod.
        """

        pod, err = await self.repo.create(
            name=req.name,
            description=req.description,
            template_ref=req.template_ref,
            cpu_lim_m_cpu=req.cpu_lim_m_cpu,
            mem_lim_mb=req.mem_lim_mb,
            storage_lim_mb=req.storage_lim_mb,
            username=req.username,
            timeout_s=req.timeout_s,
            values=req.values,
        )

        # if success, trigger pod create event
        if err is None:
            await app.add_task(
                handle_pod_create_update_event(
                    self.parent,
                    PodCreateUpdateEvent(pod_id=pod.pod_id, username=pod.username)
                )
            )

        return pod, err

    async def update(self,
                     app: Sanic,
                     req: PodUpdateRequest) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Update a pod.
        """

        pod, err = await self.repo.update(
            pod_id=req.pod_id,
            name=req.name,
            description=req.description,
            username=req.username,
            timeout_s=req.timeout_s,
            target_status=req.target_status,
        )

        # if success and target_status is pending, trigger pod create event
        if err is None and pod.resource_status == datamodels.ResourceStatusEnum.pending:
            await app.add_task(
                handle_pod_create_update_event(
                    self.parent,
                    PodCreateUpdateEvent(pod_id=pod.pod_id, username=pod.username)
                )
            )

        return pod, err

    async def delete(self,
                     app: Sanic,
                     req: PodDeleteRequest) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Delete a pod.
        """

        pod, err = await self.repo.delete(pod_id=req.pod_id)

        # if success, trigger pod delete event
        if err is None:
            await app.add_task(
                handle_pod_delete_event(self.parent, PodDeleteEvent(pod_id=pod.pod_id, username=pod.username))
            )

        return pod, err
