import json
from hashlib import sha256
from typing import List, Tuple, Optional, Dict, Any

import aio_pika
import bcrypt
from loguru import logger
from pamqp.commands import Basic

from .repo import Repo
import src.components.datamodels as datamodels
import src.components.events as events
import src.components.config as config
import pymongo

from ...components import errors
from ...components.utils import singleton


@singleton
class UserRepo:
    def __init__(self, db: Repo):
        self.db = db

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

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

        try:
            message = aio_pika.Message(
                body=events.UserCreateEvent(
                    username=username,
                ).model_dump_json().encode()
            )
            ret = await (await self.db.get_mq_channel()).default_exchange.publish(
                message,
                routing_key=config.CONFIG_EVENT_QUEUE_NAME
            )
            if not isinstance(ret, Basic.Ack):
                logger.error(f"publish create user event failed: {username}")
                return None, errors.unknown_error
            else:
                return user, None
        except Exception as e:
            logger.error(f"publish create user event error: {e}")
            return None, errors.unknown_error

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
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

        try:
            message = aio_pika.Message(
                body=events.UserUpdateEvent(
                    username=username,
                ).model_dump_json().encode()
            )
            ret = await (await self.db.get_mq_channel()).default_exchange.publish(
                message,
                routing_key=config.CONFIG_EVENT_QUEUE_NAME
            )
            if not isinstance(ret, Basic.Ack):
                logger.error(f"publish update user event failed: {username}")
                return None, errors.unknown_error
            else:
                return user_model, None
        except Exception as e:
            logger.error(f"publish update user event error: {e}")
            return None, errors.unknown_error

    async def delete(self, username: str) -> Tuple[Optional[datamodels.UserModel], Optional[Exception]]:
        try:
            user_collection = self.db.get_db_collection(datamodels.database_name, datamodels.user_collection_name)
            res = await user_collection.find_one({'username': username})
            if res is None:
                return None, errors.user_not_found
            else:
                ret = await user_collection.delete_one({'username': username})
                if ret is None:
                    return None, errors.unknown_error
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

        try:
            message = aio_pika.Message(
                body=events.UserDeleteEvent(
                    username=username,
                ).model_dump_json().encode()
            )
            ret = await (await self.db.get_mq_channel()).default_exchange.publish(
                message,
                routing_key=config.CONFIG_EVENT_QUEUE_NAME
            )
            if not isinstance(ret, Basic.Ack):
                logger.error(f"publish delete user event failed: {username}")
                return None, errors.unknown_error
            else:
                return datamodels.UserModel(**res), None
        except Exception as e:
            logger.error(f"publish delete user event error: {e}")
            return None, errors.unknown_error
