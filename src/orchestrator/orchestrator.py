import json

from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from typing import Coroutine, Any, Union
import asyncio

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
import kubernetes
import motor

from src.apiserver.repo import Repo, UserRepo, TemplateRepo
from src.components import config
from src.components.config import BackendConfig
from src.components.events import event_deserialize
from src.components.logging import create_logger
from src.components.tasks import check_kubernetes_connection
from src.orchestrator.handlers import get_event_handler


class EventOrchestrator:
    def __init__(self, opt: BackendConfig):
        self.repo = Repo(opt.to_sanic_config())

    async def handle(self, message: Union[AbstractIncomingMessage, Coroutine[Any, Any, AbstractIncomingMessage]]):
        ev, err = event_deserialize(message.body)
        if err is not None:
            logger.error(f" [x] Received {message.body}, got deserialize error {str(err)}")
            await message.ack()
            return
        else:
            logger.debug(f" [x] Received {message.body}")
            err = await get_event_handler(ev.type)(ev)
            if err is not None:
                logger.error(f" [x] Received {message.body}, got operation error {str(err)}")
                return
            else:
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
