import asyncio
import threading
import time
from typing import Optional

from loguru import logger
import pymongo

from src.components.config import BackendConfig
from src.components import datamodels, config
from src.components.utils import get_k8s_client
# from src.components.events import (
#     PodTimeoutEvent
# )
# from src.apiserver.service.handler import (
#     handle_pod_timeout_event
# )


def check_and_create_admin_user(opt: BackendConfig) -> Optional[Exception]:
    # establish MongoDB connection
    _db_url = f'mongodb://{opt.db_username}:{opt.db_password}@{opt.db_host}:{opt.db_port}'
    logger.info(f"connecting to MongoDB at {_db_url}")
    conn = pymongo.MongoClient(_db_url, connect=True)

    # check global collection
    col = conn[opt.db_database][datamodels.global_collection_name]
    try:
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
    except Exception as e:
        logger.exception(e)
        return e


def check_kubernetes_connection(opt: BackendConfig) -> Optional[Exception]:
    logger.info(f"connecting to K8S cluster at {opt.k8s_host}:{opt.k8s_port}")

    v1 = get_k8s_client(opt.k8s_host, opt.k8s_port, opt.k8s_ca_cert, opt.k8s_token, debug=False).CoreV1Api()
    try:
        _ = v1.list_namespaced_pod(namespace=config.CONFIG_PROJECT_NAME)
    except Exception as e:
        logger.exception(e)
        return e
    return None


# async def scan_pods(opt: BackendConfig, stop_ev: threading.Event = None) -> None:
#     while True:
#         await asyncio.sleep(10)
#         if stop_ev is not None and stop_ev.is_set():
#             break
