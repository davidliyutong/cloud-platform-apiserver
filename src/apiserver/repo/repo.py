import asyncio
from typing import Dict

from kubernetes import client
from aio_pika.abc import AbstractRobustChannel, AbstractQueue
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.components.utils import singleton, get_k8s_api
import aio_pika


@singleton
class Repo:
    """
    About motor's doc: https://github.com/mongodb/motor
    """
    _db: Dict[str, AsyncIOMotorDatabase] = {}
    _db_collection: Dict[str, AsyncIOMotorCollection] = {}
    _mq: AbstractRobustChannel = None
    _mq_queue: Dict[str, AbstractQueue] = {}
    _v1: client.CoreV1Api = None

    motor_uri = ''
    pika_uri = ''

    options = {}

    def __init__(self, options):
        self.motor_uri = ''
        self.options = options

    def get_db_client(self) -> AsyncIOMotorClient:
        # motor
        self.motor_uri = 'mongodb://{account}{host}:{port}'.format(
            account='{username}:{password}@'.format(
                username=self.options['DB_USERNAME'],
                password=self.options['DB_PASSWORD']) if self.options['DB_USERNAME'] else '',
            host=self.options['DB_HOST'] if self.options['DB_HOST'] else '127.0.0.1',
            port=self.options['DB_PORT'] if self.options['DB_PORT'] else 27017)
        return AsyncIOMotorClient(self.motor_uri)

    def get_db(self, db: str) -> AsyncIOMotorDatabase:
        """
        :param db: database name
        :return: the motor db instance
        """
        if db not in self._db.keys():
            self._db[db] = self.get_db_client()[db]

        return self._db[db]

    def get_db_collection(self, db_name: str, collection: str) -> AsyncIOMotorCollection:
        """
        :param db_name: database name
        :param collection: collection name
        :return: the motor collection instance
        """
        collection_key = db_name + collection
        if collection_key not in self._db_collection.keys():
            self._db_collection[collection_key] = self.get_db(db_name)[collection]

        return self._db_collection[collection_key]

    async def get_mq_channel(self) -> AbstractRobustChannel:
        self.pika_uri = 'amqp://{account}{host}:{port}'.format(
            account='{username}:{password}@'.format(
                username=self.options['MQ_USERNAME'],
                password=self.options['MQ_PASSWORD']) if self.options['MQ_USERNAME'] else '',
            host=self.options['MQ_HOST'] if self.options['MQ_HOST'] else '127.0.0.1',
            port=self.options['MQ_PORT'] if self.options['MQ_PORT'] else 5672)
        if self._mq is None:
            self._mq = await (await aio_pika.connect_robust(self.pika_uri)).channel()
        return self._mq

    async def get_mq_queue(self, queue_name: str) -> AbstractQueue:
        if queue_name not in self._mq_queue.keys():
            self._mq_queue[queue_name] = await (await self.get_mq_channel()).declare_queue(
                queue_name,
                durable=True,
            )
        return self._mq_queue[queue_name]

    async def get_k8s_api(self):
        if self._v1 is None:
            self._v1 = get_k8s_api(self.options['K8S_HOST'],
                                   self.options['K8S_PORT'],
                                   self.options['K8S_CACERT'],
                                   self.options['K8S_TOKEN'])

        return self._v1
