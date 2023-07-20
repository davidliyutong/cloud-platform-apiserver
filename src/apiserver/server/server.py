from sanic import Sanic
from src.apiserver.controller import controller_app
from src.components.config import BackendConfig
from loguru import logger
import pymongo
import src.components.datamodels as datamodels
from sanic_jwt import initialize
from src.components.authz import (
    MyJWTConfig,
    MyJWTAuthentication,
    MyJWTResponse,
    authenticate,
    store_refresh_token,
    retrieve_refresh_token
)


def prepare_run(opt: BackendConfig) -> Sanic:
    controller_app.ctx.opt = opt

    # establish MongoDB connection and attach to context
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
        global_doc = conn[opt.db_database][datamodels.global_collection_name].find_one_and_update({"_id": "global"},
                                                                                                  {"$inc": {
                                                                                                      "uid_counter": 1}})
        super_admin_user = datamodels.new_user_model(
            uid=global_doc["uid_counter"],
            username=opt.bootstrap_admin_username,
            password=opt.bootstrap_admin_password,
            role=datamodels.RoleEnum.super_admin,
        )
        col.insert_one(super_admin_user.model_dump())

    # establish Kubernetes connection and attach to context

    # Install JWT authentication
    initialize(controller_app,
               authenticate=authenticate,
               authentication_class=MyJWTAuthentication,
               configuration_class=MyJWTConfig,
               responses_class=MyJWTResponse,
               retrieve_refresh_token=retrieve_refresh_token,
               store_refresh_token=store_refresh_token)

    controller_app.config.update({'JWT_SECRET': controller_app.ctx.auth.config.secret._value})

    return controller_app
