import asyncio
import http

import jwt
from loguru import logger
from sanic import Blueprint
from sanic.server.websockets.impl import WebsocketImplProtocol
from sanic_ext import openapi

from src.apiserver.service import get_root_service
from src.apiserver.service.handler import handle_user_heartbeat_event
from src.components.events import UserHeartbeatEvent

bp = Blueprint("heartbeat", url_prefix="/heartbeat", version=1)


async def sender(ws: WebsocketImplProtocol, username: str):
    srv = get_root_service()
    ev = UserHeartbeatEvent(username=username)
    while True:
        try:
            await ws.send('ping')
            await handle_user_heartbeat_event(srv, ev)
            await asyncio.sleep(60)
        except Exception as e:
            logger.exception(e)
            break


@bp.websocket("/user", name="heartbeat_user")
@openapi.parameter("token", str, location="query", required=True)
async def user_heartbeat_ws(request, ws):
    task_name = f"receiver:{request.id}"
    token = request.args.get("token")
    if token is None:
        return http.HTTPStatus.UNAUTHORIZED
    else:
        try:
            payload = jwt.decode(token, request.app.config.get('JWT_SECRET'), algorithms='HS256')
        except Exception as e:
            logger.exception(e)
            return http.HTTPStatus.UNAUTHORIZED
        username = payload.get('username')
        if username is None:
            return http.HTTPStatus.UNAUTHORIZED

    request.app.add_task(sender(ws, username), name=task_name)
    try:
        while True:
            await ws.recv()
    finally:
        await request.app.cancel_task(task_name)
        request.app.purge_tasks()
