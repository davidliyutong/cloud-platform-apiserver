"""
This module implements the heartbeat controller.
"""

import asyncio
import http
from typing import Optional, Union

import jwt
from loguru import logger
from sanic import Blueprint
from sanic.server.websockets.impl import WebsocketImplProtocol
from sanic_ext import openapi

from src.apiserver.service import RootService
from src.components import config
from src.components.auth.common import JWT_SECRET_KEYNAME, JWT_ALGORITHM_KEYNAME
from src.components.events import UserHeartbeatEvent

bp = Blueprint("heartbeat", url_prefix="/heartbeat", version=1)


async def handle_user_heartbeat_event(srv: RootService, ev: UserHeartbeatEvent) -> Optional[Exception]:
    # list pods
    # TODO Fix this mechanism
    _, pods, err = await srv.pod_service.repo.list(extra_query_filter={"$and": [
        {'username': ev.username},
        {'current_status': 'running'}
    ]})
    if err is not None:
        logger.error(f"handle_user_heartbeat_event failed to list pods: {err}")
        return err

    # update running pod.access_at owned by current user
    tasks = [srv.pod_service.repo.update(pod_id=pod.pod_id) for pod in pods]
    await asyncio.gather(*tasks)
    return None


async def sender(ws: WebsocketImplProtocol, username: str):
    # get root service
    srv = RootService()
    ev = UserHeartbeatEvent(username=username)
    while True:
        try:
            # send ping message
            await ws.send('')
            # TODO Fix this mechanism
            # err = await handle_user_heartbeat_event(srv, ev)  # update user's heartbeat timestamp
            # if err is not None:
            #     logger.error(f"failed to update user's heartbeat timestamp: {err}")
            #     break
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
            payload = jwt.decode(
                token,
                request.app.config.get(JWT_SECRET_KEYNAME),
                algorithms=request.app.config.get(JWT_ALGORITHM_KEYNAME)
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
