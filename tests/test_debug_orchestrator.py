import asyncio
import time
import aio_pika

URL = "amqp://clpl:clpl@127.0.0.1:5672/"


async def main():
    connection = await aio_pika.connect_robust(URL)

    async with connection:
        routing_key = "clpl_event_queue"
        channel = await connection.channel()
        for _ in range(5):
            message_body = '{"type": "user_create_event", "username": "admin"}'

            message = aio_pika.Message(body=message_body.encode())
            await channel.default_exchange.publish(message, routing_key=routing_key)
            print(" [x] Sent %r" % message.body)
            time.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
