"""
This module is the entry point of the API server.
"""

import base64
import secrets

import shortuuid
from loguru import logger
from odmantic import AIOEngine
from sanic import Sanic
from sanic_jwt import initialize

from src.apiserver.controller import controller_app
from src.apiserver.controller.admin_pod import bp as admin_pod_bp
from src.apiserver.controller.admin_template import bp as admin_template_bp
from src.apiserver.controller.auth import bp as auth_bp
from src.apiserver.controller.auth_oidc import bp as auth_oidc_bp, OAuth2Config
from src.apiserver.controller.heartbeat import bp as heartbeat_bp
from src.apiserver.controller.nonadmin_pod import bp as nonadmin_pod_bp
from src.apiserver.controller.nonadmin_template import bp as nonadmin_template_bp
from src.apiserver.controller.user import bp as user_bp
from src.apiserver.controller.policy import bp as policy_bp
from src.apiserver.service import init_root_service
from src.components.auth.common import JWT_SECRET_KEYNAME, JWT_ALGORITHM_KEYNAME
from src.components.config import APIServerConfig, OIDCConfig, CONFIG_PROJECT_NAME, SiteConfig
from src.components.datamodels import database_name
from src.components.tasks import check_and_create_admin_user, check_kubernetes_connection
from src.components.tasks.crash import check_crash_flag
from src.components.tasks.sanity_check import check_rbac_readiness, check_and_create_system_document
from src.components.utils import get_k8s_client, get_async_mongo_db_connection


def apiserver_check_option(opt: APIServerConfig) -> APIServerConfig:
    """
    Check and set default values for options
    """
    # Check Token Secret
    if opt.config_token_secret is None or len(opt.config_token_secret) == 0:
        logger.warning("Token secret is not set, use random string as token secret")
        opt.config_token_secret = base64.encodebytes(secrets.token_bytes(64))
    else:
        opt.config_token_secret = base64.encodebytes(opt.config_token_secret.encode('utf-8'))

    _client = get_k8s_client(opt)
    _v1 = _client.CustomObjectsApi()

    # check existence of OIDCConfig in cluster
    try:
        crd = _v1.get_namespaced_custom_object(f'{CONFIG_PROJECT_NAME}.davidliyutong.github.io', 'v1',
                                               opt.k8s_namespace, 'oidcconfigs', opt.oidc_config_name)
        opt.oidc_config = OIDCConfig(**(crd['items'][0]['spec']))
    except Exception as e:
        logger.warning("Exception when calling get_namespaced_custom_object: %s\n" % e)
        opt.oidc_config = None

    # check existence of SiteConfig in cluster
    try:
        crd = _v1.get_namespaced_custom_object(f'{CONFIG_PROJECT_NAME}.davidliyutong.github.io', 'v1',
                                               opt.k8s_namespace, 'siteconfigs', opt.site_config_name)
        opt.site_config = SiteConfig(**(crd['items'][0]['spec']))
    except Exception as e:
        logger.warning("Exception when calling get_namespaced_custom_object: %s\n" % e)
        opt.site_config = None

    return opt


def apiserver_prepare_run(opt: APIServerConfig) -> Sanic:
    """
    Prepare to run the server
    """
    ret, err = opt.verify()
    if err is not None:
        logger.error(f"invalid option: {str(err)}")
        exit(1)
    else:
        logger.info(f"option validation succeed")

    # set options
    controller_app.ctx.opt = opt

    # Set shortuuid alphabet
    shortuuid.set_alphabet('abcdefghijklmnopqrstuvwxyz0123456789')

    # establish MongoDB connection, check and create admin user
    err = check_and_create_admin_user(opt)
    if err is not None:
        logger.error(f"task check_and_create_admin_user failed: {err}")
        exit(1)

    # check Kubernetes connection
    err = check_kubernetes_connection(opt)
    if err is not None:
        logger.error("failed to list pods in namespace, check kubernetes connection or cluster configuration")
        exit(1)

    # check system document
    err = check_and_create_system_document(opt)
    if err is not None:
        logger.error(f"task check_and_create_system_document failed: {err}")
        exit(1)

    err = check_and_create_admin_user(opt)
    if err is not None:
        logger.error(f"task check_and_create_admin_user failed: {err}")
        exit(1)

    # check existence of crash flag
    err = check_crash_flag(controller_app)
    if err is not None:
        logger.error(f"task check_crash_flag failed: {err}")
        exit(1)

    # check availability of rbac server
    err = check_rbac_readiness(opt)
    if err is not None:
        logger.error(f"task check_rbac_readiness failed: {err}")
        exit(1)

    controller_app.ext.openapi.add_security_scheme(
        "token",
        "http",
        bearer_format="JWT",
        scheme="bearer",
        location="header",
        name="Authorization"
    )
    controller_app.ext.openapi.add_security_scheme(
        "http_basic",
        "http",
        scheme="basic",
    )

    # attach Blueprint to context
    controller_app.blueprint(admin_pod_bp)
    controller_app.blueprint(admin_template_bp)
    controller_app.blueprint(auth_bp)
    if opt.config_use_oidc:
        controller_app.blueprint(auth_oidc_bp)
        controller_app.ctx.oauth_cfg = OAuth2Config.from_oidc_config(opt.oidc_config)
        controller_app.ctx.oauth_client = controller_app.ctx.oauth_cfg.get_async_client()
    controller_app.blueprint(user_bp)
    controller_app.blueprint(nonadmin_template_bp)
    controller_app.blueprint(nonadmin_pod_bp)
    controller_app.blueprint(heartbeat_bp)
    controller_app.blueprint(policy_bp)

    # attach JWT secret to context
    controller_app.config.update({JWT_SECRET_KEYNAME: opt.config_token_secret})
    controller_app.config.update({JWT_ALGORITHM_KEYNAME: 'HS256'})

    # create services
    db = get_async_mongo_db_connection(opt)
    engine = AIOEngine(client=db, database=database_name)

    _ = init_root_service(
        opt,
        engine,
        get_k8s_client(opt, opt.debug)
    )

    # this task is added to be executed after the server starts
    # FIXME: deprecate this task
    # controller_app.add_task(
    #     PodScanTask(opt=opt, sem=multiprocessing.Semaphore(1))
    # )

    return controller_app
