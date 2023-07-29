import http

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
    logger = create_logger()
    logger.info(f"creating sanic application: {application}")
    logger.info("main process start")
