"""
This module is the entry point of the API server.
"""

import base64
import secrets

import shortuuid
from loguru import logger
from sanic import Sanic
from sanic_jwt import initialize

from src.apiserver.controller import controller_app
from src.apiserver.controller.admin_pod import bp as admin_pod_bp
from src.apiserver.controller.admin_template import bp as admin_template_bp
from src.apiserver.controller.admin_user import bp as admin_user_bp
from src.apiserver.controller.auth import bp as auth_bp
from src.apiserver.controller.auth_oidc import bp as auth_oidc_bp, OAuth2Config
from src.apiserver.controller.heartbeat import bp as heartbeat_bp
from src.apiserver.controller.nonadmin_pod import bp as nonadmin_pod_bp
from src.apiserver.controller.nonadmin_template import bp as nonadmin_template_bp
from src.apiserver.controller.nonadmin_user import bp as nonadmin_user_bp
from src.apiserver.repo import DBRepo, UserRepo, TemplateRepo, PodRepo
from src.apiserver.service import RootService
from src.apiserver.service.service import new_root_service
from src.components.authn import (
    MyJWTConfig,
    MyJWTAuthentication,
    MyJWTResponse,
    authenticate,
    store_refresh_token,
    retrieve_refresh_token
)
from src.components.config import APIServerConfig
from src.components.tasks import check_and_create_admin_user, check_kubernetes_connection  # check_rabbitmq_connection
from src.components.utils import get_k8s_client

_service: RootService


def apiserver_check_option(opt: APIServerConfig) -> APIServerConfig:
    """
    Check and set default values for options
    """
    # Check Token Secret
    if opt.config_token_secret is None or len(opt.config_token_secret) == 0:
        logger.warning("Token secret is not set, use random string as token secret")
        opt.config_token_secret = base64.encodebytes(secrets.token_bytes(32))
    else:
        opt.config_token_secret = base64.encodebytes(opt.config_token_secret.encode('utf-8'))

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

    # install JWT authentication
    initialize(controller_app,
               secret=opt.config_token_secret,
               authenticate=authenticate,
               authentication_class=MyJWTAuthentication,
               configuration_class=MyJWTConfig,
               responses_class=MyJWTResponse,
               retrieve_refresh_token=retrieve_refresh_token,
               store_refresh_token=store_refresh_token)
    controller_app.ext.openapi.add_security_scheme(
        "token",
        "http",
        bearer_format="JWT",
        scheme="bearer",
        location="header",
        name="Authorization"
    )

    # attach Blueprint to context
    controller_app.blueprint(admin_pod_bp)
    controller_app.blueprint(admin_template_bp)
    controller_app.blueprint(admin_user_bp)
    controller_app.blueprint(auth_bp)
    if opt.config_use_oidc:
        controller_app.blueprint(auth_oidc_bp)
        controller_app.ctx.oauth_cfg = OAuth2Config.from_apiserver_config(opt)
        controller_app.ctx.oauth_client = controller_app.ctx.oauth_cfg.get_async_client()
    controller_app.blueprint(nonadmin_user_bp)
    controller_app.blueprint(nonadmin_template_bp)
    controller_app.blueprint(nonadmin_pod_bp)
    controller_app.blueprint(heartbeat_bp)

    # attach JWT secret to context
    controller_app.config.update({'JWT_SECRET': controller_app.ctx.auth.config.secret._value})
    controller_app.config.update({'JWT_ALGORITHM': controller_app.ctx.auth.config.algorithm._value})

    # create services
    repo = DBRepo(opt.to_sanic_config())
    _ = new_root_service(
        opt,
        UserRepo(repo),
        TemplateRepo(repo),
        PodRepo(repo),
        get_k8s_client(opt.k8s_host, opt.k8s_port, opt.k8s_ca_cert, opt.k8s_token, opt.k8s_verify_ssl, opt.debug)
    )

    return controller_app
