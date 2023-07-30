from typing import Callable, Optional, Union, Any, Coroutine

import kubernetes
from loguru import logger
from pydantic import BaseModel

from src.apiserver.repo import Repo
from src.components.events import UserCreateEvent
from src.apiserver.service import get_root_service


async def handle_user_create_event(ev: Union[UserCreateEvent, BaseModel]) -> Optional[Exception]:
    srv = get_root_service()
    user, err = await srv.admin_user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"creating k8s credentials for user {ev.username}")
    # TODO: finish
    return None


def get_event_handler(event_type: str) -> Callable[[BaseModel], Coroutine[Any, Any, Optional[Exception]]]:
    if event_type == "user_create_event":
        return handle_user_create_event
    else:
        # TODO: finish
        raise RuntimeError(f"unknown event type {event_type}")
