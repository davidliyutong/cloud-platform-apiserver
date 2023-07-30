from loguru import logger
from sanic import Sanic
from src.apiserver.controller import controller_app
from src.apiserver.service import RootService
from src.apiserver.repo import Repo, UserRepo, TemplateRepo
from src.apiserver.service.service import new_root_service
from src.components.config import BackendConfig
from sanic_jwt import initialize
from src.components.authz import (
    MyJWTConfig,
    MyJWTAuthentication,
    MyJWTResponse,
    authenticate,
    store_refresh_token,
    retrieve_refresh_token
)
from src.apiserver.controller.admin_pod import bp as admin_pod_bp
from src.apiserver.controller.admin_template import bp as admin_template_bp
from src.apiserver.controller.admin_user import bp as admin_user_bp
from src.apiserver.controller.auth import bp as auth_bp
from src.apiserver.controller.nonadmin_user import bp as nonadmin_user_bp
from src.apiserver.controller.nonadmin_pod import bp as nonadmin_pod_bp

from src.components.tasks import check_and_create_admin_user, check_kubernetes_connection
from src.components.utils import get_k8s_api
from src.orchestrator import EventOrchestrator

_service: RootService


def apiserver_prepare_run(opt: BackendConfig) -> Sanic:
    controller_app.ctx.opt = opt

    # establish MongoDB connection, check and create admin user
    _ = check_and_create_admin_user(opt)

    # Install JWT authentication
    initialize(controller_app,
               authenticate=authenticate,
               authentication_class=MyJWTAuthentication,
               configuration_class=MyJWTConfig,
               responses_class=MyJWTResponse,
               retrieve_refresh_token=retrieve_refresh_token,
               store_refresh_token=store_refresh_token)

    # attach Blueprint to context
    controller_app.blueprint(admin_pod_bp)
    controller_app.blueprint(admin_template_bp)
    controller_app.blueprint(admin_user_bp)
    controller_app.blueprint(auth_bp)
    controller_app.blueprint(nonadmin_user_bp)
    controller_app.blueprint(nonadmin_pod_bp)

    # attach JWT secret to context
    controller_app.config.update({'JWT_SECRET': controller_app.ctx.auth.config.secret._value})

    # create services
    _ = new_root_service(
        UserRepo(Repo(controller_app.config)),
        TemplateRepo(Repo(controller_app.config))
    )

    return controller_app


def orchestrator_prepare_run(opt: BackendConfig) -> EventOrchestrator:
    import logging
    logging.getLogger("pika").setLevel(logging.WARNING)

    # establish Kubernetes connection and attach to context
    err = check_kubernetes_connection(opt)
    if err is not None:
        logger.exception(err)
        exit(1)

    repo = Repo(opt.to_sanic_config())
    _ = new_root_service(
        UserRepo(repo),
        TemplateRepo(repo),
        get_k8s_api(opt.k8s_host, opt.k8s_port, opt.k8s_ca_cert, opt.k8s_token)
    )

    return EventOrchestrator(opt)
