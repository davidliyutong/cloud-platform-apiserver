"""
This module contains tasks that are executed periodically / once.
"""
import asyncio
import datetime
from typing import List

import sanic
from loguru import logger

from src.components.types import PodUpdateRequest
from src.components import config
from src.components.datamodels import PodModelV1, PodStatusEnum
from .common import AsyncTask


class PodScanTask(AsyncTask):

    async def loop(self, app: sanic.Sanic) -> None:
        from src.apiserver.service import RootService
        running_pods: List[PodModelV1]
        logger.info("pod scanning task started")
        await asyncio.sleep(5)  # delay for a short while
        while True:
            try:
                srv = RootService()
                _, running_pods, _ = await srv.pod_service.repo.list(extra_query_filter={"current_status": "running"})
                now = datetime.datetime.utcnow()

                # filter timeouted pods
                out_pods = filter(
                    lambda pod: pod.accessed_at + datetime.timedelta(seconds=pod.timeout_s) < now,
                    running_pods
                )

                # shut-em down
                tasks = [
                    srv.pod_service.update(app,
                                           PodUpdateRequest(pod_id=pod.pod_id, target_status=PodStatusEnum.stopped))
                    for pod in out_pods]
                await asyncio.gather(*tasks)
                logger.info(f"pod scanning task looped, {len(tasks)} pods stopped")
            except asyncio.CancelledError:
                logger.info("pod scanning task cancelled")
                break
            except Exception as e:
                logger.exception(e)

            await asyncio.sleep(config.CONFIG_SCAN_POD_INTERVAL_S)
