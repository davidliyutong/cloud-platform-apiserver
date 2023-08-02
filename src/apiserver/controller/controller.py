"""
This module defines the controller of the apiserver.
"""
import http

from loguru import logger
from sanic import Sanic
from sanic.response import json as json_response

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
async def main_process_start(application):
    """
    This function is called when the main process starts.
    """
    logger.info(f"sanic application: {application} started")
