import datetime
from typing import Dict, Optional

from .common import ServiceInterface


class HeartbeatService(ServiceInterface):
    def __init__(self):
        super().__init__()
        self._db: Dict[str, datetime.datetime] = {}

    async def ping(self, key: str) -> Optional[Exception]:
        self._db[key] = datetime.datetime.utcnow()
        return None
