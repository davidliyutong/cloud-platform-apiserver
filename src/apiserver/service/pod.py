"""
Pod service
"""
from enum import Enum
import json
from typing import Tuple, Union

from loguru import logger
from sanic import Sanic

from src.apiserver.controller.types import *
from src.apiserver.repo import PodRepo
from src.components import datamodels, errors
from src.components.events import PodCreateUpdateEvent, PodDeleteEvent
from .common import ServiceInterface
from .handler import handle_pod_create_update_event, handle_pod_delete_event


class ModeEnum(str, Enum):
    create = "create"
    update = "update"


class PodService(ServiceInterface):
    def __init__(self, pod_repo: PodRepo):
        super().__init__()
        self.repo: PodRepo = pod_repo

    @staticmethod
    def check_quota(
            user: datamodels.UserModel,
            pods: List[datamodels.PodModel],
            req: Union[PodCreateRequest, PodUpdateRequest],
            mode: ModeEnum
    ) -> bool:
        if user.quota is None:
            return True

        if mode == ModeEnum.create:
            # Create mode: only check pod count and storage (total across all pods)
            # CPU/mem/GPU checks are deferred to when the pod is started (update to running)
            num_pods = len(pods) + 1
            storage_mb = sum([pod.storage_lim_mb for pod in pods]) + req.storage_lim_mb

            if any([
                num_pods > user.quota.pod_n,
                storage_mb > user.quota.storage_mb,
            ]):
                return False
            return True

        elif mode == ModeEnum.update:
            if req.target_status != datamodels.PodStatusEnum.running:
                return True

            # Update to running: check cpu/mem/gpu against running pods only
            running_pods = list(
                filter(
                    lambda x: x.current_status == datamodels.PodStatusEnum.running and x.pod_id != req.pod_id,
                    pods
                )
            )
            req_gpu = req.gpu if req.gpu is not None else 0
            cpu_m = sum([pod.cpu_lim_m_cpu for pod in running_pods]) + req.cpu_lim_m_cpu
            mem_mb = sum([pod.mem_lim_mb for pod in running_pods]) + req.mem_lim_mb
            storage_mb = sum([pod.storage_lim_mb for pod in pods])
            gpu = sum([pod.gpu for pod in running_pods]) + req_gpu

            if any([
                cpu_m > user.quota.cpu_m,
                mem_mb > user.quota.memory_mb,
                storage_mb > user.quota.storage_mb,
                gpu > user.quota.gpu,
            ]):
                return False
            return True

        else:
            return False

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
                     req: PodCreateRequest) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Create a pod.
        """
        # read username from request
        if req.username is None or req.username == "":
            return None, errors.username_required

        # check if user exists and is active
        user, err = await self.parent.user_service.repo.get(username=req.username)
        if any([
            err is not None,
            user is not None and user.status != datamodels.UserStatusEnum.active,
        ]):
            return None, errors.user_not_found

        # list all pods of the user
        _, pods, err = await self.parent.pod_service.repo.list(extra_query_filter={"username": req.username})

        # check if user has reached the quota
        ret = self.check_quota(user, pods, req, mode=ModeEnum.create)
        if not ret:
            return None, errors.quota_exceeded

        pod, err = await self.repo.create(
            name=req.name,
            description=req.description,
            template_ref=req.template_ref,
            cpu_lim_m_cpu=req.cpu_lim_m_cpu,
            mem_lim_mb=req.mem_lim_mb,
            storage_lim_mb=req.storage_lim_mb,
            gpu=req.gpu,
            username=req.username,
            user_uuid=str(user.uuid),
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
        old_pod, err = await self.repo.get(req.pod_id)
        if err is not None:
            return None, errors.pod_not_found

        if req.username is None or req.username == "":
            req.username = old_pod.username

        user, err = await self.parent.user_service.repo.get(username=req.username)
        if any([
            err is not None,
            user is not None and user.status != datamodels.UserStatusEnum.active,
        ]):
            return None, errors.user_not_found
        else:
            req.user_uuid = str(user.uuid)

        # list all pods of the user
        _, pods, err = await self.parent.pod_service.repo.list(extra_query_filter={"username": req.username})

        # check if user has reached the quota
        req.cpu_lim_m_cpu = old_pod.cpu_lim_m_cpu
        req.mem_lim_mb = old_pod.mem_lim_mb
        req.storage_lim_mb = old_pod.storage_lim_mb
        req.gpu = old_pod.gpu

        ret = self.check_quota(user, pods, req, mode=ModeEnum.update)
        if not ret:
            return None, errors.quota_exceeded

        pod, err = await self.repo.update(
            pod_id=req.pod_id,
            name=req.name,
            description=req.description,
            username=req.username,
            user_uuid=req.user_uuid,
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
