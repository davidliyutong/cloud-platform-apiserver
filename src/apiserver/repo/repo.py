from typing import Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.components.utils import singleton


@singleton
class Repo:
    """
    About motor's doc: https://github.com/mongodb/motor
    """
    _db: Dict[str, AsyncIOMotorDatabase] = {}
    _collection: Dict[str, AsyncIOMotorCollection] = {}
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
        if collection_key not in self._collection.keys():
            self._collection[collection_key] = self.get_db(db_name)[collection]

        return self._collection[collection_key]
