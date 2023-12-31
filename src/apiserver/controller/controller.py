"""
This module defines the controller of the apiserver.
"""
import http
import sys

from loguru import logger
from sanic import Sanic
from sanic.response import json as json_response

from src.components import config
from src.components.config import APIServerConfig
from src.components.tasks import set_crash_flag, get_crash_flag, recover_from_crash, scan_pods
from .types import OIDCStatusResponse

app = Sanic("root")


def _health(opt: APIServerConfig):
    return json_response(
        {
            'description': '/health',
            'status': http.HTTPStatus.OK,
            'message': "OK",
            'version': config.CONFIG_BUILD_VERSION,
            'config': {
                'coder_hostname': opt.config_coder_hostname,
                'vnc_hostname': opt.config_vnc_hostname,
                'ssh_hostname': opt.config_ssh_hostname,
            },
            'oidc': None if not opt.config_use_oidc else OIDCStatusResponse(
                name=opt.oidc_name,
                path=app.url_for("root.auth_oidc.login")  # "/v1/auth/oidc/login"
            ).model_dump()
        },
        http.HTTPStatus.OK
    )


@app.get("/health", name="health")
async def health(request):
    """
    Health check. Return a 200 OK response.
    """
    return _health(request.app.ctx.opt)


@app.get("/health", name="v1_health", version=1)
async def health(request):
    """
    Health check. Return a 200 OK response.
    """
    return _health(request.app.ctx.opt)


@app.main_process_start
async def main_process_start(application: Sanic):
    """
    This function is called when the main process starts.
    """
    logger.info(f"sanic application: {application} starting")


@app.main_process_stop
async def main_process_stop(application: Sanic):
    """
    This function is called when the main process stops.
    """
    logger.info(f"sanic application: {application} stopping")
    application.shutdown_tasks(timeout=config.CONFIG_SHUTDOWN_GRACE_PERIOD_S)

    # set crash flag to False
    _ = await set_crash_flag(application.ctx.opt, False)


@app.after_server_start
async def after_server_start(application: Sanic):
    """
    This function is called after the server starts.
    """
    logger.info(f"sanic process: {application.m.name} started")

    # only check crash status in rank 0 process
    if application.m.name == "Sanic-Server-0-0":
        # check if apiserver crashed last time
        crashed, err = await get_crash_flag(application.ctx.opt)
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
            ret, err = await recover_from_crash(application)
            if not ret:
                logger.error(err)
                sys.exit(1)
            else:
                logger.info("apiserver recovered from crash")

        # set crash flag to True, assume will crash
        _ = await set_crash_flag(application.ctx.opt, True)

    # only start scan_pods task in rank 0 process
    if application.m.name == "Sanic-Server-0-0":
        await application.add_task(scan_pods(application), name="scan_pods")


@app.before_server_stop
async def before_server_stop(application: Sanic):
    # only cancel scan_pods task in rank 0 process
    if application.m.name == "Sanic-Server-0-0":
        await application.cancel_task("scan_pods")
        await application.purge_tasks()
