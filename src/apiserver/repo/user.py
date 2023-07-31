import json
from hashlib import sha256
from typing import List, Tuple, Optional, Dict, Any

import bcrypt
from bson import ObjectId
from loguru import logger

from .repo import Repo
import src.components.datamodels as datamodels
import pymongo

from src.components import errors
from src.components.utils import singleton


@singleton
class UserRepo:
    def __init__(self, db: Repo):
        self.db = db

    async def _commit(self, db_id: ObjectId) -> None:
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
        ret = collection.find_one_and_update(
            {"_id": db_id},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            logger.error(f"commit error")
            raise errors.unknown_error

    async def commit(self, username: str) -> None:
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
        ret = collection.find_one_and_update(
            {"username": username},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            raise errors.unknown_error
        else:
            return None

    async def get(self, username) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        res = await self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name).find_one(
            {'username': username})
        if res is None:
            return None, errors.user_not_found
        else:
            return datamodels.UserModel(**res), None

    async def list(self,
                   index_start: int = -1,
                   index_end: int = -1,
                   extra_query_filter_str: str = "") -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:

        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            num_document = await collection.count_documents({})

            # assemble query filter
            _start = 0 if index_start < 0 else index_start
            _end = num_document if index_end < 0 else index_end

            query_filter = {}
            if extra_query_filter_str != "":
                try:
                    json.loads(extra_query_filter_str)
                    query_filter = json.loads(extra_query_filter_str)
                except json.JSONDecodeError:
                    logger.error(f"extra_query_filter_str is not a valid json string: {extra_query_filter_str}")
                    return num_document, [], errors.wrong_query_filter

            res = []
            cursor = collection.find(query_filter).sort('uid', pymongo.ASCENDING)
            async for document in cursor:
                res.append(datamodels.UserModel(**document))
            return num_document, res[_start:_end], None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return 0, [], errors.db_connection_error

    async def create(self,
                     username: str,
                     password: str,
                     email: str,
                     role: str,
                     quota: Dict[str, Any]) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        try:
            user_collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            global_collection = self.db.get_db_collection(datamodels.database_name, datamodels.global_collection_name)

            # check if username exists
            if await user_collection.count_documents({'username': username}) > 0:
                return None, errors.duplicate_username

            global_doc = await global_collection.find_one_and_update(
                {"_id": "global"},
                {"$inc": {
                    "uid_counter": 1}})
            uid = global_doc["uid_counter"]

            user = datamodels.UserModel.new(
                uid=uid,
                username=username,
                password=password,
                role=datamodels.RoleEnum(role),
                email=email,
                quota=quota
            )

            ret = await user_collection.insert_one(user.model_dump())
            if ret is None:
                return None, errors.db_connection_error
            else:
                return user, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def update(self,
                     username: str,
                     password: Optional[str],
                     status: Optional[str],
                     email: Optional[str],
                     role: Optional[str],
                     quota: Optional[Dict[str, Any]]) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            if await collection.count_documents({'username': username}) <= 0:
                return None, errors.user_not_found

            user = await collection.find_one({'username': username})

            try:
                user['password'] = sha256(password.encode()).hexdigest() if password is not None else user['password']
                user['htpasswd'] = f"{username}:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt(
                    rounds=12)).decode() if password is not None else user['htpasswd']
                user['status'] = status if status is not None else user['status']
                user['email'] = email if email is not None else user['email']
                user['role'] = datamodels.RoleEnum(role) if role is not None else user['role']
                user['quota'] = quota if quota is not None else user['quota']
                user_model = datamodels.UserModel(**user)  # check if the user model is valid
            except Exception as _:
                return None, errors.wrong_user_profile

            ret = await collection.find_one_and_replace({'_id': user['_id']}, user)
            if ret is None:
                logger.error(f"update user unknown error: {username}")
                return None, errors.unknown_error
            else:
                return user_model, None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def delete(self, username: str) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            res = await collection.find_one({'username': username})
            if res is None:
                return None, errors.user_not_found
            else:
                user = datamodels.UserModel(**res)
                ret = await collection.find_one_and_update(
                    {'username': username},
                    {'$set': {'resource_status': 'deleted'}})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return user, None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def purge(self, username: str) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            res = await collection.find_one({'username': username})
            if res is None:
                return None, errors.user_not_found
            else:
                user = datamodels.UserModel(**res)
                ret = await collection.delete_one({'username': username})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return user, None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error
