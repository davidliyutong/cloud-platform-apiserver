import multiprocessing as mp
from typing import Optional

import sanic
from loguru import logger
from odmantic import SyncEngine

from src.components import datamodels
from src.components.config import APIServerConfig
from src.components.utils import get_mongo_db_connection
from src.rbacserver.adapters import get_text_policy_iterator
from src.rbacserver.controller.controller import app as controller_app
from src.rbacserver.controller.enforce import bp as enforce_bp
from src.rbacserver.controller.policy import bp as policy_bp
from src.rbacserver.defaults import system_policy_text
from src.rbacserver.tasks import RBACWorkerSyncTask


def check_and_create_rbac_config(opt: APIServerConfig) -> Optional[Exception]:
    # establish MongoDB connection
    engine = SyncEngine(get_mongo_db_connection(opt), database=opt.db_database)

    try:
        res = engine.find_one(datamodels.RBACPolicyModelV2, {"name": "default"})
        if res is None:
            logger.info("default policy not found, creating...")
            p = datamodels.RBACPolicyModelV2(
                name="default",
                description="default policy",
                policies=list(
                    get_text_policy_iterator(system_policy_text)
                ),
                resource_status=datamodels.ResourceStatusEnum.committed
            )
            engine.save(p)
        return None
    except Exception as e:
        logger.exception(e)
        return e


def rbac_server_prepare_run(opt: APIServerConfig) -> sanic.Sanic:
    """
    Prepare to run the server
    """
    # set options
    controller_app.ctx.opt = opt

    err = check_and_create_rbac_config(opt)
    if err is not None:
        logger.error(f"task check_and_create_admin_user failed: {err}")
        exit(1)

    controller_app.blueprint(policy_bp)
    controller_app.blueprint(enforce_bp)

    # build enforcer after server starts
    controller_app.ctx.enforcer = None
    # for multi-worker mode, use shared_ctx to notify all workers to update the policy
    if opt.rbac_num_workers > 1:
        controller_app.shared_ctx.update_notification_queue = mp.Queue()

    controller_app.add_task(
        RBACWorkerSyncTask(opt=opt)
    )
    return controller_app


def rbac_server_check_option(opt: APIServerConfig):
    return opt
