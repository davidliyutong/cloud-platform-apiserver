from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from typing import Coroutine, Any, Union
import asyncio

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from src.components import config
from src.components.config import BackendConfig
from src.components.logging import create_logger
from src.components.tasks import check_kubernetes_connection


class EventOrchestrator:
    async def handle(self, message: Union[AbstractIncomingMessage, Coroutine[Any, Any, AbstractIncomingMessage]]):
        logger.debug(" [x] Received %r" % message.body)
        await message.ack()

    async def run(self, opt: BackendConfig):
        logger = create_logger("./logs/orchestrator")
        logger.info("orchestrator started")

        _ = check_kubernetes_connection(opt)

        pika_uri = 'amqp://{account}{host}:{port}'.format(
            account='{username}:{password}@'.format(
                username=opt.mq_username,
                password=opt.mq_password) if opt.mq_username else '',
            host=opt.mq_host if opt.mq_host else '127.0.0.1',
            port=opt.mq_port if opt.mq_port else 5672)

        connection = await aio_pika.connect_robust(pika_uri)

        async with connection:
            queue_name = config.CONFIG_EVENT_QUEUE_NAME
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name)
            loop = asyncio.get_running_loop()

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    loop.create_task(self.handle(message))
