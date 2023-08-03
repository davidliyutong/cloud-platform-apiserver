"""
Heartbeat service
"""

import asyncio
import datetime
from typing import Dict, Optional

from .common import ServiceInterface


class HeartbeatService(ServiceInterface):
    def __init__(self):
        super().__init__()
        self._db: Dict[str, datetime.datetime] = {}

    async def ping(self, username: str) -> Optional[Exception]:
        srv = self.parent
        # list pods
        _, pods, err = await srv.pod_service.repo.list(extra_query_filter={"$and": [
            {'username': username},
            {'current_status': 'running'}
        ]})
        if err is not None:
            return err

        # update running pod.access_at owned by current user
        tasks = [srv.pod_service.repo.update(pod_id=pod.pod_id) for pod in pods]
        await asyncio.gather(*tasks)
        return None
