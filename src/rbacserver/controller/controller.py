"""
This module defines the controller of the rbacserver.
"""
import asyncio
import http

from loguru import logger
from sanic import Sanic
from sanic.response import json as json_response

from src.components.config import APIServerConfig
from src.rbacserver.adapters import build_casbin_enforcer

app = Sanic("rbacserver")

from src import CONFIG_BUILD_VERSION


def _health(opt: APIServerConfig):
    return json_response(
        {
            'description': '/health',
            'status': http.HTTPStatus.OK,
            'message': "OK",
            'version': CONFIG_BUILD_VERSION,
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
    logger.info(f"sanic process: {application.name} started")

    # enforcer is not fork safe, so we need to re-establish the connection
    application.ctx.enforcer = build_casbin_enforcer(application.ctx.opt)

    # load the policy manually since we use custom adapter
    await application.ctx.enforcer.load_policy()

    # compute the rank of the worker
    if application.ctx.opt.rbac_num_workers > 1:
        application.ctx.rank = int(application.m.name.split("-")[2])


@app.before_server_stop
async def before_server_stop(application: Sanic):
    """
    This function is called after the server stops.
    """
    logger.info(f"sanic process: {application.name} stopped")
