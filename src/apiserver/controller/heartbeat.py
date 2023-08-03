"""
This module implements the heartbeat controller.
"""

import asyncio
import http

import jwt
from loguru import logger
from sanic import Blueprint
from sanic.server.websockets.impl import WebsocketImplProtocol
from sanic_ext import openapi

from src.apiserver.service import get_root_service
from src.apiserver.service.handler import handle_user_heartbeat_event
from src.components import config
from src.components.events import UserHeartbeatEvent

bp = Blueprint("heartbeat", url_prefix="/heartbeat", version=1)


async def sender(ws: WebsocketImplProtocol, username: str):
    # get root service
    srv = get_root_service()
    ev = UserHeartbeatEvent(username=username)
    while True:
        try:
            # send ping message
            await ws.send('ping')
            await handle_user_heartbeat_event(srv, ev)  # update user's heartbeat timestamp
            await asyncio.sleep(config.CONFIG_HEARTBEAT_INTERVAL_S)  # wait for 120 seconds
        except Exception as e:
            logger.error(f"connection closed: {e}")
            break


@bp.websocket("/user", name="heartbeat_user")
@openapi.definition(
    parameter=[
        openapi.definitions.Parameter("token", str, location="query", required=True),
    ]
)
async def user_heartbeat_ws(request, ws: WebsocketImplProtocol):
    """
    User heartbeat websocket. The serve will send a 'ping' message to the client every 60 seconds.

    If the client does not recv within 60 seconds, the server will close the connection.

    If the client responds with ACK, the server will update the user's heartbeat timestamp.
    """
    task_name = f"receiver:{request.id}"

    # parse query args, token should be encoded jwt
    token = request.args.get("token")
    if token is None or token == "":
        return http.HTTPStatus.UNAUTHORIZED
    else:
        try:
            # decode jwt token
            # attention: request.app.config.get('JWT_SECRET') is created by sanic-jwt and attached to the app at startup
            # attention: request.app.config.get('JWT_ALGORITHM') is created by sanic-jwt and attached to the app at \
            # startup
            payload = jwt.decode(
                token,
                request.app.config.get('JWT_SECRET'),
                algorithms=request.app.config.get('JWT_ALGORITHM')
            )
        except Exception as e:
            logger.error(f"failed to decode jwt token: {e}")
            return http.HTTPStatus.UNAUTHORIZED

        # get username from payload
        username = payload.get('username')
        if username is None:
            return http.HTTPStatus.UNAUTHORIZED

    # start sender task with username
    request.app.add_task(sender(ws, username), name=task_name)
    try:
        while True:
            await ws.recv()
    finally:
        # await request.app.cancel_task(task_name)
        request.app.purge_tasks()
