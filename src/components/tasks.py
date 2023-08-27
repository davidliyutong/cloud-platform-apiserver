"""
This module contains tasks that are executed periodically / once.
"""
import asyncio
import datetime
from typing import Optional, Tuple, List

import pymongo
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic

from src.apiserver.controller.types import PodUpdateRequest
from src.apiserver.service import get_root_service
from src.apiserver.service.handler import (
    handle_user_update_event,
    handle_user_delete_event,
    handle_template_update_event,
    handle_template_delete_event,
    handle_pod_create_update_event,
    handle_pod_delete_event
)
from src.components import datamodels, config
from src.components.config import APIServerConfig
from src.components.datamodels import PodModel, PodStatusEnum
from src.components.events import (
    UserUpdateEvent,
    UserDeleteEvent,
    TemplateUpdateEvent,
    TemplateDeleteEvent,
    PodCreateUpdateEvent,
    PodDeleteEvent
)
from src.components.utils import get_k8s_client


def get_mongo_db_connection(opt: APIServerConfig) -> pymongo.MongoClient:
    """
    Get MongoDB connection
    """
    _db_uri = f'mongodb://{opt.db_username}:{opt.db_password}@{opt.db_host}:{opt.db_port}'
    logger.debug(f"connecting to MongoDB at {_db_uri}")
    conn = pymongo.MongoClient(_db_uri, connect=True)
    return conn


def get_async_mongo_db_connection(opt: APIServerConfig) -> AsyncIOMotorClient:
    """
    Get MongoDB connection Async
    """
    _db_uri = f'mongodb://{opt.db_username}:{opt.db_password}@{opt.db_host}:{opt.db_port}'
    logger.debug(f"connecting to MongoDB at {_db_uri}")
    return AsyncIOMotorClient(_db_uri)


def check_and_create_admin_user(opt: APIServerConfig) -> Optional[Exception]:
    """
    Check if admin user exists in DB, if not, create one.
    """

    # establish MongoDB connection
    conn = get_mongo_db_connection(opt)

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
                role=datamodels.UserRoleEnum.super_admin,
            )
            col.insert_one(super_admin_user.model_dump())
        return None
    except Exception as e:
        logger.exception(e)
        return e


async def set_crash_flag(opt: APIServerConfig, flag: bool) -> Optional[Exception]:
    conn = get_async_mongo_db_connection(opt)
    col = conn[opt.db_database][datamodels.global_collection_name]
    try:
        logger.info(f"setting crash flag to {flag}")
        await col.update_one({"_id": "global"}, {"$set": {"flag_crashed": flag}})
    except Exception as e:
        logger.exception(e)
        return e


async def get_crash_flag(opt: APIServerConfig) -> Tuple[bool, Optional[Exception]]:
    conn = get_async_mongo_db_connection(opt)
    col = conn[opt.db_database][datamodels.global_collection_name]
    try:
        doc = await col.find_one({"_id": "global"})
        logger.info(f"crash flag is {bool(doc['flag_crashed'])}")
        return bool(doc["flag_crashed"]), None
    except Exception as e:
        logger.exception(e)
        return True, e


def check_kubernetes_connection(opt: APIServerConfig) -> Optional[Exception]:
    """
    Check if the connection to Kubernetes cluster is valid.
    """

    logger.info(f"connecting to K8S cluster at {opt.k8s_host}:{opt.k8s_port}")

    v1 = get_k8s_client(opt.k8s_host, opt.k8s_port, opt.k8s_ca_cert, opt.k8s_token, debug=False).CoreV1Api()
    try:
        _ = v1.list_namespaced_pod(namespace=opt.k8s_namespace)
    except Exception as e:
        logger.exception(e)
        return e
    return None


async def recover_from_crash(app: Sanic) -> Tuple[bool, Optional[Exception]]:
    """
    Recover from crash.
    """
    logger.info("recovering from crash...")
    srv = get_root_service()

    tasks = []
    # query database
    _uncommitted_users = srv.user_service.repo.list(extra_query_filter={"resource_status": "pending"})
    _deleted_users = srv.user_service.repo.list(extra_query_filter={"resource_status": "deleted"})
    _uncommitted_templates = srv.template_service.repo.list(extra_query_filter={"resource_status": "pending"})
    _deleted_templates = srv.template_service.repo.list(extra_query_filter={"resource_status": "deleted"})
    _uncommitted_pods = srv.pod_service.repo.list(extra_query_filter={"resource_status": "pending"})
    _deleted_pods = srv.pod_service.repo.list(extra_query_filter={"resource_status": "deleted"})

    # wait until complete
    _, uncommitted_users, _ = await _uncommitted_users
    logger.info(f"uncommitted users: {uncommitted_users}")
    _, deleted_users, _ = await _deleted_users
    logger.info(f"deleted users: {deleted_users}")
    _, uncommitted_templates, _ = await _uncommitted_templates
    logger.info(f"uncommitted templates: {uncommitted_templates}")
    _, deleted_templates, _ = await _deleted_templates
    logger.info(f"deleted templates: {deleted_templates}")
    _, uncommitted_pods, _ = await _uncommitted_pods
    logger.info(f"uncommitted pods: {uncommitted_pods}")
    _, deleted_pods, _ = await _deleted_pods

    loop = asyncio.get_running_loop()

    # check users
    for user in uncommitted_users:
        tasks.append(loop.create_task(handle_user_update_event(srv, UserUpdateEvent(username=user.username))))
    for user in deleted_users:
        tasks.append(loop.create_task(handle_user_delete_event(srv, UserDeleteEvent(username=user.username))))

    # check templates
    for template in uncommitted_templates:
        tasks.append(loop.create_task(
            handle_template_update_event(srv, TemplateUpdateEvent(template_id=template.template_id))
        ))
    for template in deleted_templates:
        tasks.append(loop.create_task(
            handle_template_delete_event(srv, TemplateDeleteEvent(template_id=template.template_id))
        ))

    # check pods
    for pod in uncommitted_pods:
        tasks.append(loop.create_task(
            handle_pod_create_update_event(srv, PodCreateUpdateEvent(pod_id=pod.pod_id, username=pod.username))
        ))
    for pod in deleted_pods:
        tasks.append(loop.create_task(
            handle_pod_delete_event(srv, PodDeleteEvent(pod_id=pod.pod_id, username=pod.username))
        ))

    # wait until complete
    await asyncio.gather(*tasks)

    return True, None


async def scan_pods(app: Sanic) -> None:
    running_pods: List[PodModel]
    logger.info("pod scanning task started")
    await asyncio.sleep(5)  # delay for a short while
    while True:
        try:
            srv = get_root_service()
            _, running_pods, _ = await srv.pod_service.repo.list(extra_query_filter={"current_status": "running"})
            now = datetime.datetime.utcnow()

            # filter timeouted pods
            out_pods = filter(
                lambda pod: pod.accessed_at + datetime.timedelta(seconds=pod.timeout_s) < now,
                running_pods
            )

            # shut-em down
            tasks = [
                srv.pod_service.update(app, PodUpdateRequest(pod_id=pod.pod_id, target_status=PodStatusEnum.stopped))
                for pod in out_pods]
            await asyncio.gather(*tasks)
            logger.info(f"pod scanning task looped, {len(tasks)} pods stopped")
        except asyncio.CancelledError:
            logger.info("pod scanning task cancelled")
            break
        except Exception as e:
            logger.exception(e)

        await asyncio.sleep(config.CONFIG_SCAN_POD_INTERVAL_S)
