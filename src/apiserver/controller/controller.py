"""
This module defines the controller of the apiserver.
"""
import asyncio
import http

from loguru import logger
from sanic import Sanic
from sanic.response import json as json_response

from src.components import config
from src.components.config import APIServerConfig
from src.components.tasks.crash import set_crash_flag_async
from src.components.types.common import OIDCStatusResponse

app = Sanic("apiserver")

from src import CONFIG_BUILD_VERSION


def _health(opt: APIServerConfig):
    return json_response(
        {
            'description': '/health',
            'status': http.HTTPStatus.OK,
            'message': "OK",
            'version': CONFIG_BUILD_VERSION,
            'config': {
                'coder_hostname': opt.site_config.coder_hostname,
                'vnc_hostname': opt.site_config.vnc_hostname,
                'ssh_hostname': opt.site_config.ssh_hostname,
            },
            'oidc': None if not opt.config_use_oidc else OIDCStatusResponse(
                name=opt.oidc_config.name,
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
    err = await set_crash_flag_async(application.ctx.opt, False)
    if err is not None:
        logger.error(f"failed to set crash flag to False: {err}")
    else:
        logger.info(f"sanic application: {application} stopped")

    # kill the workers by force
    for count_down in range(3, 0, -1):
        logger.info(f"kill workers in {count_down} seconds")
        await asyncio.sleep(1)
    application.manager.kill()


@app.after_server_start
async def after_server_start(application: Sanic):
    """
    This function is called after the server starts.
    """
    try:
        _ = application.m
        logger.info(f"sanic process: {application.m.name} started")
    except AttributeError:
        pass


@app.before_server_stop
async def before_server_stop(application: Sanic):
    """
    This function is called after the server stops.
    """
    try:
        _ = application.m
        logger.info(f"sanic process: {application.m.name} stopped")
    except AttributeError:
        pass
