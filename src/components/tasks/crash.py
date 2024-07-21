import asyncio
from typing import Optional, Tuple

import sanic
from loguru import logger


from src.components.utils import get_async_mongo_db_connection, get_mongo_db_connection
from src.components.config import APIServerConfig
from src.components.datamodels.names import system_collection_name, system_document_name


async def set_crash_flag_async(opt: APIServerConfig, flag: bool) -> Optional[Exception]:
    conn = get_async_mongo_db_connection(opt)
    col = conn[opt.db_database][system_collection_name]
    try:
        logger.info(f"setting crash flag to {flag}")
        await col.update_one({"_name": system_document_name}, {"$set": {"status": {"flag_crashed": flag}}})
    except Exception as e:
        logger.exception(e)
        return e


async def get_crash_flag_async(opt: APIServerConfig) -> Tuple[bool, Optional[Exception]]:
    conn = get_async_mongo_db_connection(opt)
    col = conn[opt.db_database][system_collection_name]
    try:
        doc = await col.find_one({"_name": system_document_name})
        res = bool(doc['status']['flag_crashed'])
        logger.info(f"crash flag is {res}")
        return res, None
    except Exception as e:
        logger.exception(e)
        return True, e


def set_crash_flag(opt: APIServerConfig, flag: bool) -> Optional[Exception]:
    conn = get_mongo_db_connection(opt)
    col = conn[opt.db_database][system_collection_name]
    try:
        logger.info(f"setting crash flag to {flag}")
        col.update_one({"_name": system_document_name}, {"$set": {"status": {"flag_crashed": flag}}})
    except Exception as e:
        logger.exception(e)
        return e


def get_crash_flag(opt: APIServerConfig) -> Tuple[bool, Optional[Exception]]:
    conn = get_mongo_db_connection(opt)
    col = conn[opt.db_database][system_collection_name]
    try:
        doc = col.find_one({"_name": system_document_name})
        res = bool(doc['status']['flag_crashed'])
        logger.info(f"crash flag is {res}")
        return res, None
    except Exception as e:
        logger.exception(e)
        return True, e


def _recover_from_crash(app: sanic.Sanic) -> Tuple[bool, Optional[Exception]]:
    """
    Recover from crash. TODO: implement this.
    """
    # logger.info("recovering from crash...")
    # srv = RootService()
    #
    # tasks = []
    # # query database
    # _uncommitted_users = srv.user_service.repo.list(extra_query_filter={"resource_status": "pending"})
    # _deleted_users = srv.user_service.repo.list(extra_query_filter={"resource_status": "deleted"})
    # _uncommitted_templates = srv.template_service.repo.list(extra_query_filter={"resource_status": "pending"})
    # _deleted_templates = srv.template_service.repo.list(extra_query_filter={"resource_status": "deleted"})
    # _uncommitted_pods = srv.pod_service.repo.list(extra_query_filter={"resource_status": "pending"})
    # _deleted_pods = srv.pod_service.repo.list(extra_query_filter={"resource_status": "deleted"})
    #
    # # wait until complete
    # _, uncommitted_users, _ = await _uncommitted_users
    # logger.info(f"uncommitted users: {uncommitted_users}")
    # _, deleted_users, _ = await _deleted_users
    # logger.info(f"deleted users: {deleted_users}")
    # _, uncommitted_templates, _ = await _uncommitted_templates
    # logger.info(f"uncommitted templates: {uncommitted_templates}")
    # _, deleted_templates, _ = await _deleted_templates
    # logger.info(f"deleted templates: {deleted_templates}")
    # _, uncommitted_pods, _ = await _uncommitted_pods
    # logger.info(f"uncommitted pods: {uncommitted_pods}")
    # _, deleted_pods, _ = await _deleted_pods
    #
    # loop = asyncio.get_running_loop()
    #
    # # check users
    # for user in uncommitted_users:
    #     tasks.append(loop.create_task(handle_user_update_event(srv, UserUpdateEvent(username=user.username))))
    # for user in deleted_users:
    #     tasks.append(loop.create_task(handle_user_delete_event(srv, UserDeleteEvent(username=user.username))))
    #
    # # check templates
    # for template in uncommitted_templates:
    #     tasks.append(loop.create_task(
    #         handle_template_update_event(srv, TemplateUpdateEvent(template_id=template.template_id))
    #     ))
    # for template in deleted_templates:
    #     tasks.append(loop.create_task(
    #         handle_template_delete_event(srv, TemplateDeleteEvent(template_id=template.template_id))
    #     ))
    #
    # # check pods
    # for pod in uncommitted_pods:
    #     tasks.append(loop.create_task(
    #         handle_pod_create_update_event(srv, PodCreateUpdateEvent(pod_id=pod.pod_id, username=pod.username))
    #     ))
    # for pod in deleted_pods:
    #     tasks.append(loop.create_task(
    #         handle_pod_delete_event(srv, PodDeleteEvent(pod_id=pod.pod_id, username=pod.username))
    #     ))
    #
    # # wait until complete
    # await asyncio.gather(*tasks)

    return True, None


def check_crash_flag(app: sanic.Sanic) -> Optional[Exception]:
    # check if apiserver crashed last time
    crashed, err = get_crash_flag(app.ctx.opt)
    if err is not None:
        logger.warning(f"cannot get crash_flag: {err}")
        crashed = True

    # if crashed, print warning
    if crashed:
        logger.warning("apiserver crashed last time")
    else:
        logger.info("apiserver did not crash last time")

    # recover from crash
    if crashed:
        ret, err = _recover_from_crash(app)
        if not ret:
            logger.error(err)
            return err
        else:
            logger.info("apiserver recovered from crash")

    # set crash flag to True, assume will crash
    _ = set_crash_flag(app.ctx.opt, True)
    return None
