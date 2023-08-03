"""
UserRepo is a class that provides methods to access the database for user related operations.
"""

from hashlib import sha256
from typing import List, Tuple, Optional, Dict, Any

import bcrypt
import pymongo
from loguru import logger

import src.components.datamodels as datamodels
from src.components import errors
from src.components.utils import singleton
from .db import DBRepo


@singleton
class UserRepo:
    def __init__(self, db: DBRepo):
        self.db = db

    async def commit(self, username: str) -> None:
        """
        Commit a user, set its resource_status to committed.
        """
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
        ret = collection.find_one_and_update(
            {"username": username},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            raise errors.unknown_error
        else:
            return None

    async def get(self, username: str) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        """
        Get a user by username.
        """
        res = await self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name).find_one(
            {'username': username})
        if res is None:
            return None, errors.user_not_found
        else:
            return datamodels.UserModel(**res), None

    async def list(
            self,
            index_start: int = -1,
            index_end: int = -1,
            extra_query_filter: Dict[str, Any] = None
    ) -> Tuple[int, List[datamodels.UserModel], Optional[Exception]]:
        """
        List users.
        """

        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            num_document = await collection.count_documents({})

            # assemble query filter
            _start = 0 if index_start < 0 else index_start
            _end = num_document if index_end < 0 else index_end
            query_filter = {} if extra_query_filter is None else extra_query_filter

            cursor = collection.find(query_filter).sort('uid', pymongo.ASCENDING)

            # read from cursor
            res = []
            async for document in cursor:
                res.append(datamodels.UserModel(**document))

            # return sliced result
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
        """
        Create a user.
        """
        try:
            # mongodb collection
            user_collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            global_collection = self.db.get_db_collection(datamodels.database_name, datamodels.global_collection_name)

            # check if username exists
            if await user_collection.count_documents({'username': username}) > 0:
                return None, errors.duplicate_username

            # calculate uid
            global_doc = await global_collection.find_one_and_update(
                {"_id": "global"},
                {"$inc": {
                    "uid_counter": 1}})
            uid = global_doc["uid_counter"]

            # build user model
            user = datamodels.UserModel.new(
                uid=uid,
                username=username,
                password=password,
                role=datamodels.UserRoleEnum(role),
                email=email,
                quota=quota
            )

            # insert into database
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
        """
        Update a user.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)

            # check if username exists
            if await collection.count_documents({'username': username}) <= 0:
                return None, errors.user_not_found

            # get user
            user = await collection.find_one({'username': username})

            # noinspection PyBroadException
            try:
                user['password'] = sha256(password.encode()).hexdigest() if password is not None else user['password']
                user['htpasswd'] = f"{username}:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt(
                    rounds=12)).decode() if password is not None else user['htpasswd']
                user['status'] = status if status is not None else user['status']
                user['email'] = email if email is not None else user['email']
                user['role'] = datamodels.UserRoleEnum(role) if role is not None else user['role']
                user['quota'] = quota if quota is not None else user['quota']

                # if password is changed, then set resource_status to pending
                if any([
                    password is not None,
                ]):
                    user['resource_status'] = datamodels.ResourceStatusEnum.pending.value

                # check if the user model is valid
                user_model = datamodels.UserModel(**user)  # check if the user model is valid

            except Exception as e:
                logger.error(f"update user {username} wrong profile: {e}")
                return None, errors.wrong_user_profile

            # update user
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
        """
        Delete a user. (set resource_status to deleted)
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)

            # check if user exists
            res = await collection.find_one({'username': username})
            if res is None:
                return None, errors.user_not_found
            else:
                # build user model
                user = datamodels.UserModel(**res)

                # delete user (set resource_status to deleted)
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
        """
        Purge a user.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)

            # check if user exists
            res = await collection.find_one({'username': username})
            if res is None:
                return None, errors.user_not_found
            else:
                # build user model
                user = datamodels.UserModel(**res)

                # delete user
                ret = await collection.delete_one({'username': username})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return user, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error
