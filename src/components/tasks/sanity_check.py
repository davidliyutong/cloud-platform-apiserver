"""
This module contains tasks that are executed periodically / once.
"""
from typing import Optional
import time
import requests

from loguru import logger
from odmantic import SyncEngine

import src
from src.components import datamodels
from src.components.config import APIServerConfig
from src.components.datamodels import system_document_name
from src.components.datamodels.group import GroupEnumInternal
from src.components.utils import get_k8s_client, get_mongo_db_connection
from src.components.utils.security import get_hashed_text


def check_and_create_system_document(opt: APIServerConfig) -> Optional[Exception]:
    """
    Check if system document exists in DB, if not, create one.
    """
    engine = SyncEngine(get_mongo_db_connection(opt), database=opt.db_database)

    try:
        res = engine.find_one(
            datamodels.SystemModel,
            datamodels.SystemModel.name == system_document_name
        )
        if res is None:
            logger.info("default system document not found, creating...")
            p = datamodels.SystemModel(
                status=datamodels.SystemStatusModel(),
                settings=datamodels.SystemSettingsModel()
            )
            engine.save(p)
        else:
            logger.info("default system document found")
            if res.status.version != src.CONFIG_BUILD_VERSION:
                logger.warning("system document version mismatch, aborting...")
                return ValueError("system document version mismatch")
        return None
    except Exception as e:
        logger.exception(e)
        return e


def check_and_create_admin_user(opt: APIServerConfig) -> Optional[Exception]:
    """
    Check if admin user exists in DB, if not, create one.
    """

    engine = SyncEngine(get_mongo_db_connection(opt), database=opt.db_database)

    try:
        res = engine.find_one(
            datamodels.UserModelV2,
            datamodels.UserModelV2.username == opt.bootstrap_admin_username
        )
        if res is None:
            logger.info("admin user not found, creating...")
            p = datamodels.UserModelV2(
                username=opt.bootstrap_admin_username,
                group=GroupEnumInternal.admin,
                password=get_hashed_text(opt.bootstrap_admin_password),
                role=datamodels.UserRoleEnum.super_admin,
            )
            engine.save(p)
        return None
    except Exception as e:
        logger.exception(e)
        return e


def check_kubernetes_connection(opt: APIServerConfig) -> Optional[Exception]:
    """
    Check if the connection to Kubernetes cluster is valid.
    """

    logger.info(f"connecting to K8S cluster at {opt.k8s_host}:{opt.k8s_port}")

    v1 = get_k8s_client(opt, debug=False).CoreV1Api()
    try:
        _ = v1.list_namespaced_pod(namespace=opt.k8s_namespace)
    except Exception as e:
        logger.exception(e)
        return e
    return None


def check_rbac_readiness(opt: APIServerConfig, timeout: int = 5) -> Optional[Exception]:
    url = f'http://127.0.0.1:{opt.rbac_port}/health'
    start_time = time.time()
    with requests.Session() as session:
        while True:
            if time.time() - start_time > timeout:
                return TimeoutError(f"Request timed out after {timeout} seconds")
            try:
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                if response.status_code == 200:
                    return None
            except requests.HTTPError:
                continue
            except requests.RequestException:
                continue
            finally:
                time.sleep(1)
