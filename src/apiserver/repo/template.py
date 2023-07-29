import json
from typing import List, Tuple, Optional, Dict, Any

import aio_pika
from loguru import logger
from pamqp.commands import Basic

from .repo import Repo
import src.components.datamodels as datamodels
import pymongo

from ...components import errors, events, config
from ...components.utils import singleton


@singleton
class TemplateRepo:
    def __init__(self, db: Repo):
        self.db = db

    async def get(self, template_id) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        res = await self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name).find_one(
            {'template_id': template_id})
        if res is None:
            return None, errors.template_not_found
        else:
            return datamodels.TemplateModel(**res), None

    async def list(self,
                   index_start: int = -1,
                   index_end: int = -1,
                   extra_query_filter_str: str = "") -> Tuple[int, List[datamodels.TemplateModel], Optional[Exception]]:

        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)
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
            cursor = collection.find(query_filter).sort('template_id', pymongo.ASCENDING)
            async for document in cursor:
                res.append(datamodels.TemplateModel(**document))
            return num_document, res[_start:_end], None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return 0, [], errors.db_connection_error

    async def create(self,
                     template_name: str,
                     description: str,
                     image_ref: str,
                     template_str: str,
                     fields: Optional[Dict[str, Any]],
                     defaults: Optional[Dict[str, Any]]) -> Tuple[
        Optional[datamodels.TemplateModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)

            template = datamodels.TemplateModel.new(
                template_name=template_name,
                description=description,
                image_ref=image_ref,
                template_str=template_str,
                fields=fields,
                defaults=defaults,
            )
            if not template.verify():
                return None, errors.template_invalid

            ret = await collection.insert_one(template.model_dump())
            if ret is None:
                return None, errors.unknown_error
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

        try:
            message = aio_pika.Message(
                body=events.TemplateCreateEvent(
                    template_id=str(template.template_id),
                ).model_dump_json().encode()
            )
            ret = await (await self.db.get_mq_channel()).default_exchange.publish(
                message,
                routing_key=config.CONFIG_EVENT_QUEUE_NAME
            )
            if not isinstance(ret, Basic.Ack):
                logger.error(f"publish create template event failed: {template_name}")
                return None, errors.unknown_error
            else:
                return template, None
        except Exception as e:
            logger.error(f"publish create template event error: {e}")
            return None, errors.unknown_error

    async def update(self,
                     template_id: str,
                     template_name: Optional[str],
                     description: Optional[str],
                     image_ref: Optional[str],
                     template_str: Optional[str],
                     fields: Optional[Dict[str, Any]],
                     defaults: Optional[Dict[str, Any]]) -> Tuple[
        Optional[datamodels.TemplateModel], Optional[Exception]]:
        try:
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)
            if await collection.count_documents({'template_id': template_id}) <= 0:
                return None, errors.template_not_found

            template = await collection.find_one({'template_id': template_id})

            try:
                template['template_name'] = template_name if template_name is not None else template['template_name']
                template['description'] = description if description is not None else template['description']
                template['image_ref'] = image_ref if image_ref is not None else template['image_ref']
                template['template_str'] = template_str if template_str is not None else template['template_str']
                template['fields'] = fields if fields is not None else template['fields']
                template['defaults'] = defaults if defaults is not None else template['defaults']
                template_model = datamodels.TemplateModel(**template)  # check if the user model is valid
                if not template_model.verify():
                    return None, errors.template_invalid
            except Exception as _:
                return None, errors.wrong_template_profile

            ret = await collection.find_one_and_replace({'_id': template['_id']}, template)
            if ret is None:
                logger.error(f"update template unknown error: {template_id}")
                return None, errors.unknown_error

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

        try:
            message = aio_pika.Message(
                body=events.TemplateUpdateEvent(
                    template_id=str(template_id),
                ).model_dump_json().encode()
            )
            ret = await (await self.db.get_mq_channel()).default_exchange.publish(
                message,
                routing_key=config.CONFIG_EVENT_QUEUE_NAME
            )
            if not isinstance(ret, Basic.Ack):
                logger.error(f"publish update template event failed: {template_name}")
                return None, errors.unknown_error
            else:
                return template_model, None
        except Exception as e:
            logger.error(f"publish update template event error: {e}")
            return None, errors.unknown_error

    async def delete(self, template_id: str) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        try:
            user_collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)
            res = await user_collection.find_one({'template_id': template_id})
            if res is None:
                return None, errors.template_not_found
            else:
                ret = await user_collection.delete_one({'template_id': template_id})
                if ret is None:
                    return None, errors.unknown_error
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

        try:
            message = aio_pika.Message(
                body=events.TemplateDeleteEvent(
                    template_id=str(template_id),
                ).model_dump_json().encode()
            )
            ret = await (await self.db.get_mq_channel()).default_exchange.publish(
                message,
                routing_key=config.CONFIG_EVENT_QUEUE_NAME
            )
            if not isinstance(ret, Basic.Ack):
                logger.error(f"publish delete template event failed: {template_id}")
                return None, errors.unknown_error
            else:
                return datamodels.TemplateModel(**res), None
        except Exception as e:
            logger.error(f"publish delete template event error: {e}")
            return None, errors.unknown_error