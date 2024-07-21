from typing import Tuple, Optional

from src.components.tasks.common import AsyncTask


class Migration_0_0_to_0_1(AsyncTask):
    """
    Migration 0.0 -> 0.1
    """

    async def loop(self, app) -> Tuple[bool, Optional[Exception]]:
        """
        Migration 0.0 -> 0.1
        """
        # TODO: implement migration 0.0 -> 0.1
        pass