import asyncio
from typing import Optional
import os

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
import pymongo
from src.components.config import BackendConfig
from src.components import datamodels, config
from src.components.errors import k8s_config_not_found


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
    # k8s_service_host = os.environ.get("KUBERNETES_SERVICE_HOST", "")
    # k8s_service_port = os.environ.get("KUBERNETES_SERVICE_PORT", "")
    # if k8s_service_host == "" or k8s_service_port == "":
    #     logger.warning("kubernetes endpoint not found")
    #     return k8s_config_not_found
    # else:
    #     logger.info(f"kubernetes endpoint configuration found: {k8s_service_host}:{k8s_service_port}")
    #     return None

    from kubernetes import client, config

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    ret = v1.list_namespace(watch=False)
    if len(ret.items) == 0:
        logger.warning("kubernetes endpoint not found")
        return k8s_config_not_found
    else:
        logger.info("kubernetes endpoint found")
        return None
