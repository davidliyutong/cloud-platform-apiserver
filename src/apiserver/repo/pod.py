"""
PodRepo is a class that provides methods to access the database for pod related operations.
"""

import datetime
from typing import List, Tuple, Optional, Dict, Any

import pymongo
from loguru import logger

import src.components.datamodels as datamodels
from src.components import errors
from src.components.utils import singleton
from .db import DBRepo


@singleton
class PodRepo:
    def __init__(self, db: DBRepo):
        self.db = db

    async def commit(self, pod_id: str) -> None:
        """
        Commit a pod, set its resource_status to committed.
        """
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
        ret = collection.find_one_and_update(
            {"pod_id": pod_id},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            raise errors.unknown_error
        else:
            return None

    async def get(self, pod_id: str) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Get a pod by pod_id.
        """
        res = await self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name).find_one(
            {'pod_id': pod_id}
        )
        if res is None:
            return None, errors.pod_not_found
        else:
            return datamodels.PodModel(**res), None

    async def list(
            self,
            index_start: int = -1,
            index_end: int = -1,
            extra_query_filter: Dict[str, Any] = None
    ) -> Tuple[int, List[datamodels.PodModel], Optional[Exception]]:
        """
        List pods.
        """

        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
            num_document = await collection.count_documents({})

            # assemble query filter
            _start = 0 if index_start < 0 else index_start
            _end = num_document if index_end < 0 else index_end
            query_filter = {} if extra_query_filter is None else extra_query_filter

            cursor = collection.find(query_filter).sort('name', pymongo.ASCENDING)

            # read from cursor
            res = []
            async for document in cursor:
                res.append(datamodels.PodModel(**document))

            # return sliced result
            return num_document, res[_start:_end], None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return 0, [], errors.db_connection_error

    async def create(self,
                     name: str,
                     description: str,
                     template_ref: str,
                     cpu_lim_m_cpu: int,
                     mem_lim_mb: int,
                     storage_lim_mb: int,
                     username: str,
                     user_uuid: str,
                     timeout_s: int,
                     values: Optional[Dict[str, Any]]) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Create a pod.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)

            # build pod model
            pod = datamodels.PodModel.new(
                template_ref=template_ref,
                username=username,
                user_uuid=user_uuid,
                name=name,
                description=description,
                cpu_lim_m_cpu=cpu_lim_m_cpu,
                mem_lim_mb=mem_lim_mb,
                storage_lim_mb=storage_lim_mb,
                timeout_s=timeout_s,
            )
            _ = values  # TODO: use these values

            # insert into database
            ret = await collection.insert_one(pod.model_dump())
            if ret is None:
                return None, errors.db_connection_error
            else:
                return pod, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def update(
            self,
            pod_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            username: Optional[str] = None,
            user_uuid: Optional[str] = None,
            timeout_s: Optional[int] = None,
            target_status: Optional[datamodels.PodStatusEnum] = None,
            started_at: Optional[datetime.datetime] = None,  # hidden argument
            accessed_at: Optional[datetime.datetime] = None,  # hidden argument
            current_status: Optional[datamodels.PodStatusEnum] = None,  # hidden argument
            template_str: Optional[str] = None,  # hidden argument
    ) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Update a pod.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)

            # check if pod exists
            if await collection.count_documents({'pod_id': pod_id}) <= 0:
                return None, errors.pod_not_found

            # get pod
            pod = await collection.find_one({'pod_id': pod_id})

            # noinspection PyBroadException
            try:
                # update pod
                pod['name'] = name if name is not None else pod['name']
                pod['description'] = description if description is not None else pod['description']
                pod['username'] = username if username is not None else pod['username']
                pod['user_uuid'] = user_uuid if user_uuid is not None else pod['user_uuid']
                pod['timeout_s'] = timeout_s if timeout_s is not None else pod['timeout_s']
                pod['target_status'] = target_status if target_status is not None else pod['target_status']

                # only controller can change the following fields
                pod['started_at'] = started_at if started_at is not None else pod['started_at']
                pod['accessed_at'] = accessed_at if accessed_at is not None else datetime.datetime.utcnow()  # auto
                pod['current_status'] = current_status if current_status is not None else pod['current_status']
                pod['template_str'] = template_str if template_str is not None else pod['template_str']

                # if username or target_status is changed, then set resource_status to pending
                if any([
                    username is not None,
                    target_status is not None,
                ]):
                    pod['resource_status'] = datamodels.ResourceStatusEnum.pending.value

                # check if the profile is valid
                pod_model = datamodels.PodModel(**pod)  # check if the pod model is valid

            except Exception as e:
                logger.error(f"update pod {pod} wrong profile: {e} ")
                return None, errors.wrong_pod_profile

            # update pod
            ret = await collection.find_one_and_replace({'_id': pod['_id']}, pod)
            if ret is None:
                logger.error(f"update pod unknown error: {pod_id}")
                return None, errors.unknown_error
            else:
                return pod_model, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def delete(self, pod_id: str) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Delete a pod. (set resource_status to deleted)
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)

            # check if pod exists
            res = await collection.find_one({'pod_id': pod_id})
            if res is None:
                return None, errors.pod_not_found
            else:
                # build pod model
                pod = datamodels.PodModel(**res)

                # delete pod (set resource_status to deleted)
                ret = await collection.find_one_and_update(
                    {'pod_id': pod_id},
                    {'$set': {'resource_status': 'deleted'}})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return pod, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def purge(self, pod_id: str) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        """
        Purge a pod.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)

            # check if pod exists
            res = await collection.find_one({'pod_id': pod_id})
            if res is None:
                return None, errors.pod_not_found
            else:
                # build pod model
                pod = datamodels.PodModel(**res)

                # delete pod
                ret = await collection.delete_one({'pod_id': pod_id})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return pod, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error
