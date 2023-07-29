from typing import Optional

from loguru import logger
import pymongo
from src.components.config import BackendConfig
from src.components import datamodels


def check_and_create_admin_user(opt: BackendConfig) -> Optional[Exception]:
    # establish MongoDB connection
    _db_url = f'mongodb://{opt.db_username}:{opt.db_password}@{opt.db_host}:{opt.db_port}'
    logger.info(f"connecting to MongoDB at {_db_url}")
    conn = pymongo.MongoClient(_db_url)

    # check global collection
    col = conn[opt.db_database][datamodels.global_collection_name]
    if len(list(col.find({}))) == 0:
        logger.info("global collection not found, creating...")
        global_doc = datamodels.GlobalModel().model_dump()
        col.insert_one({"_id": "global", **global_doc})

    # check admin user
    col = conn[opt.db_database][datamodels.user_collection_name]
    admin_user_query_result = list(col.find({"username": opt.bootstrap_admin_username}))
    if len(admin_user_query_result) == 0:
        logger.info("admin user not found, creating...")
        global_doc = conn[opt.db_database][datamodels.global_collection_name].find_one_and_update(
            {"_id": "global"},
            {"$inc": {"uid_counter": 1}}
        )
        super_admin_user = datamodels.UserModel.new(
            uid=global_doc["uid_counter"],
            username=opt.bootstrap_admin_username,
            password=opt.bootstrap_admin_password,
            role=datamodels.RoleEnum.super_admin,
        )
        col.insert_one(super_admin_user.model_dump())

    return None


def check_kubernetes_connection(opt: BackendConfig) -> Optional[Exception]:
    pass


async def create_consumer_queues(opt: BackendConfig):
    pass
