import asyncio
import multiprocessing as mp
import queue
from typing import Tuple, Optional

import sanic
from loguru import logger

from src.components.tasks import AsyncTask
from src.rbacserver.datamodels import UpdateNotificationMsg


class RBACWorkerSyncTask(AsyncTask):

    async def loop(self, app: sanic.Sanic) -> Tuple[bool, Optional[Exception]]:
        q: mp.Queue = app.shared_ctx.update_notification_queue
        finished_flag = 0
        for rank in range(app.ctx.opt.rbac_num_workers):
            finished_flag |= 1 << rank

        while True:
            if q.empty():
                await asyncio.sleep(1)
                continue
            try:
                notification: UpdateNotificationMsg = q.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.5)
                continue

            # remove if already processed
            if notification.processed_flag & finished_flag == finished_flag:
                logger.info(f"worker {app.ctx.rank} removed the notification")
                continue

            if notification.processed_flag & (1 << app.ctx.rank) == (1 << app.ctx.rank):
                # put back to the queue
                q.put(notification)
                logger.debug(f"worker {app.ctx.rank} put back the notification")
                await asyncio.sleep(1)
            else:
                if notification.sync_required:
                    notification.processed_flag |= 1 << app.ctx.rank
                    q.put(notification)
                    try:
                        await app.ctx.enforcer.load_policy()
                        logger.info(f"worker {app.ctx.rank} reloaded policy")
                    except Exception as e:
                        logger.exception(e)
                else:
                    notification.processed_flag |= 1 << app.ctx.rank
                    q.put(notification)

                    try:
                        for p in notification.policies:
                            if p[0] == "p":
                                await app.ctx.enforcer.add_policy(*p[1:])
                            elif p[0] == "g":
                                await app.ctx.enforcer.add_grouping_policy(*p[1:])
                            else:
                                logger.warning(f"unknown policy type: {p[0]}")
                            logger.debug(f"worker {app.ctx.rank} added policy {p}")
                    except Exception as e:
                        logger.exception(e)

        # noinspection PyUnreachableCode
        return True, None
