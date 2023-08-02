"""
TemplateRepo is a class that provides methods to access the database for template related operations.
"""

from typing import List, Tuple, Optional, Dict, Any

from loguru import logger

from .db import DBRepo
import src.components.datamodels as datamodels
import pymongo

from src.components import errors
from src.components.utils import singleton


@singleton
class TemplateRepo:
    def __init__(self, db: DBRepo):
        self.db = db

    async def commit(self, template_id: str) -> None:
        """
        Commit a template, set its resource_status to committed.
        """
        collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)
        ret = collection.find_one_and_update(
            {"template_id": template_id},
            {"$set": {"resource_status": datamodels.ResourceStatusEnum.committed.value}}
        )
        if ret is None:
            logger.error(f"commit error")
            raise errors.unknown_error

    async def get(self, template_id: str) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Get a template by template_id.
        """
        res = await self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name).find_one(
            {'template_id': template_id}
        )
        if res is None:
            return None, errors.template_not_found
        else:
            return datamodels.TemplateModel(**res), None

    async def list(self,
                   index_start: int = -1,
                   index_end: int = -1,
                   extra_query_filter: Dict[str, Any] = None) -> Tuple[
        int, List[datamodels.TemplateModel], Optional[Exception]]:
        """
        List templates.
        """

        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)
            num_document = await collection.count_documents({})

            # assemble query filter
            _start = 0 if index_start < 0 else index_start
            _end = num_document if index_end < 0 else index_end
            query_filter = {} if extra_query_filter is None else extra_query_filter

            cursor = collection.find(query_filter).sort('template_id', pymongo.ASCENDING)

            # read from cursor
            res = []
            async for document in cursor:
                res.append(datamodels.TemplateModel(**document))

            # return sliced result
            return num_document, res[_start:_end], None
        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return 0, [], errors.db_connection_error

    async def create(
            self,
            name: str,
            description: str,
            image_ref: str,
            template_str: str,
            fields: Optional[Dict[str, Any]],
            defaults: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Create a template.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)

            # build template model
            template = datamodels.TemplateModel.new(
                name=name,
                description=description,
                image_ref=image_ref,
                template_str=template_str,
                fields=fields,
                defaults=defaults,
            )
            # check if the template model is valid
            if not template.verify():
                return None, errors.template_invalid

            # insert into db
            ret = await collection.insert_one(template.model_dump())
            if ret is None:
                return None, errors.unknown_error
            else:
                return template, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def update(
            self,
            template_id: str,
            name: Optional[str],
            description: Optional[str],
            image_ref: Optional[str],
            template_str: Optional[str],
            fields: Optional[Dict[str, Any]],
            defaults: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Update a template.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)

            # check if the template exists
            if await collection.count_documents({'template_id': template_id}) <= 0:
                return None, errors.template_not_found

            # get the template
            template = await collection.find_one({'template_id': template_id})

            try:
                # update the template
                template['name'] = name if name is not None else template['name']
                template['description'] = description if description is not None else template['description']
                template['image_ref'] = image_ref if image_ref is not None else template['image_ref']
                template['template_str'] = template_str if template_str is not None else template['template_str']
                template['fields'] = fields if fields is not None else template['fields']
                template['defaults'] = defaults if defaults is not None else template['defaults']
                template['resource_status'] = datamodels.ResourceStatusEnum.pending.value

                # check if the template model is valid
                template_model = datamodels.TemplateModel(**template)  # check if the template model is valid
                if not template_model.verify():
                    return None, errors.template_invalid

            except Exception as e:
                logger.error(f"update template wrong profile: {e}")
                return None, errors.wrong_template_profile

            # update the template
            ret = await collection.find_one_and_replace({'_id': template['_id']}, template)
            if ret is None:
                logger.error(f"update template unknown error: {template_id}")
                return None, errors.unknown_error
            else:
                return template_model, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def delete(self, template_id: str) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Delete a template.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)

            # check if the template exists
            res = await collection.find_one({'template_id': template_id})
            if res is None:
                return None, errors.template_not_found
            else:
                # build template model
                template = datamodels.TemplateModel(**res)

                # delete the template (set resource_status to deleted)
                ret = await collection.find_one_and_update(
                    {'template_id': template_id},
                    {'$set': {'resource_status': 'deleted'}})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return template, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error

    async def purge(self, template_id: str) -> Tuple[Optional[datamodels.TemplateModel], Optional[Exception]]:
        """
        Purge a template.
        """
        try:
            # mongodb collection
            collection = self.db.get_db_collection(datamodels.database_name, datamodels.template_collection_name)

            # check if pod exists
            res = await collection.find_one({'template_id': template_id})
            if res is None:
                return None, errors.template_not_found
            else:
                # build template model
                template = datamodels.TemplateModel(**res)

                # delete template
                ret = await collection.delete_one({'template_id': template_id})
                if ret is None:
                    return None, errors.unknown_error
                else:
                    return template, None

        except Exception as e:
            logger.error(f"get_collection error: {e}")
            return None, errors.db_connection_error
