import json
from typing import List, Tuple, Optional

from loguru import logger

from .repo import Repo, singleton
import src.components.datamodels as datamodels
import pymongo

from ...components import errors


class UserRepo:
    def __init__(self, db: Repo):
        self.db = db

    async def get(self, username):
        return self.db.get_collection(datamodels.database_name, datamodels.user_collection_name).find_one(
            {'username': username})

    async def list(self,
                   uid_start: int = -1,
                   uid_end: int = -1,
                   extra_query_filter_str: str = "") -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:

        try:
            collection = self.db.get_collection(datamodels.database_name, datamodels.user_collection_name)
            num_document = await collection.count_documents({})

            # assemble query filter
            query_filter = {}
            if uid_start >= 0:
                query_filter.update({'uid': {'$gte': uid_start}})
            if uid_end >= 0:
                query_filter.update({'uid': {'$lte': uid_end}})
            if extra_query_filter_str != "":
                try:
                    json.loads(extra_query_filter_str)
                    query_filter.update({'$or': json.loads(extra_query_filter_str)})
                except json.JSONDecodeError:
                    logger.error(f"extra_query_filter_str is not a valid json string: {extra_query_filter_str}")
                    return num_document, [], errors.wrong_query_filter

            res = []
            cursor = collection.find(query_filter).sort('uid', pymongo.ASCENDING)
            async for document in cursor:
                res.append(datamodels.UserModel(**document))
            return num_document, res, None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return 0, [], errors.db_connection_error
