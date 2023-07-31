import json
from typing import List, Tuple, Optional, Dict, Any

from bson import ObjectId
from loguru import logger

from .repo import Repo
import src.components.datamodels as datamodels
import pymongo

from src.components import errors
from src.components.utils import singleton


@singleton
class PodRepo:
    def __init__(self, db: Repo):
        self.db = db

    async def _commit(self, db_id: ObjectId) -> None:
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
        ret = collection.find_one_and_update(
            {"_id": db_id},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            logger.error(f"commit error")
            raise errors.unknown_error

    async def commit(self, pod_id: str) -> None:
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
        ret = collection.find_one_and_update(
            {"pod_id": pod_id},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            raise errors.unknown_error
        else:
            return None

    async def get(self, pod_id) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        res = await self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name).find_one(
            {'pod_id': pod_id})
        if res is None:
            return None, errors.pod_not_found
        else:
            return datamodels.PodModel(**res), None

    async def list(self,
                   index_start: int = -1,
                   index_end: int = -1,
                   extra_query_filter_str: str = "") -> Tuple[int, List[datamodels.PodModel], Optional[Exception]]:

        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
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
                res.append(datamodels.PodModel(**document))
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
                     uid: int,
                     timeout_s: int,
                     values: Optional[Dict[str, Any]]) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)

            pod = datamodels.PodModel.new(
                template_ref=template_ref,
                uid=uid,
                name=name,
                description=description,
                cpu_lim_m_cpu=cpu_lim_m_cpu,
                mem_lim_mb=mem_lim_mb,
                storage_lim_mb=storage_lim_mb,
                timeout_s=timeout_s,
            )
            _ = values  # TODO: use these values

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
            name: str = None,
            description: str = None,
            uid: int = None,
            timeout_s: int = None,
            target_status: Optional[datamodels.PodStatusEnum] = None
    ) -> Tuple[Optional[datamodels.PodModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
            if await collection.count_documents({'pod_id': pod_id}) <= 0:
                return None, errors.pod_not_found

            pod = await collection.find_one({'pod_id': pod_id})

            # noinspection PyBroadException
            try:
                pod['name'] = name if name is not None else pod['name']
                pod['description'] = description if description is not None else pod['description']
                pod['uid'] = uid if uid is not None else pod['uid']
                pod['timeout_s'] = timeout_s if timeout_s is not None else pod['timeout_s']
                pod['target_status'] = target_status if target_status is not None else pod['target_status']
                pod['resource_status'] = datamodels.ResourceStatusEnum.pending.value
                pod_model = datamodels.PodModel(**pod)  # check if the pod model is valid
            except Exception as e:
                logger.error(f"update pod {pod} wrong profile: {e} ")
                return None, errors.wrong_pod_profile

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
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
            res = await collection.find_one({'pod_id': pod_id})
            if res is None:
                return None, errors.pod_not_found
            else:
                pod = datamodels.PodModel(**res)
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
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.pod_collection_name)
            res = await collection.find_one({'pod_id': pod_id})
            if res is None:
                return None, errors.pod_not_found
            else:
                pod = datamodels.PodModel(**res)
                ret = await collection.delete_one({'pod_id': pod_id})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return pod, None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error
