import http

from loguru import logger
from sanic import Sanic
from sanic.response import json as json_response

from src.components.logging import create_logger

app = Sanic("root")


@app.get("/health", name="health")
async def health(_):
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
    logger.info(f"sanic application: {application} started")
