import asyncio
import time

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
import json
from src.components import datamodels

URL = "amqp://clpl:clpl@127.0.0.1:5672/"


async def process_message(message: AbstractIncomingMessage):
    async with message.process():
        print(" [x] Received %r" % message.body)


async def main():
    connection = await aio_pika.connect_robust(URL)

    async with connection:
        queue_name = "clpl_event_queue"
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name)

        while True:
            await queue.consume(process_message)
            time.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
