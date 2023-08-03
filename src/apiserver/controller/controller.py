"""
This module defines the controller of the apiserver.
"""
import http
import sys

from loguru import logger
from sanic import Sanic
from sanic.response import json as json_response

from src.components import config
from src.components.tasks import set_crash_flag, get_crash_flag, recover_from_crash, scan_pods

app = Sanic("root")


@app.get("/health", name="health")
async def health(_):
    """
    Health check. Return a 200 OK response.
    """
    return json_response(
        {
            'description': '/health',
            'status': http.HTTPStatus.OK,
            'message': "OK"
        },
        http.HTTPStatus.OK
    )


@app.main_process_start
async def main_process_start(application: Sanic):
    """
    This function is called when the main process starts.
    """
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

    # only start scan_pods task in rank 0 process
    if application.m.name == "Sanic-Server-0-0":
        await application.add_task(scan_pods(application), name="scan_pods")


@app.before_server_stop
async def before_server_stop(application: Sanic):
    # only cancel scan_pods task in rank 0 process
    if application.m.name == "Sanic-Server-0-0":
        await application.cancel_task("scan_pods")
        await application.purge_tasks()
