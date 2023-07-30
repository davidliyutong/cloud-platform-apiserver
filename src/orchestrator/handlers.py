import base64
from typing import Callable, Optional, Union, Any, Coroutine

import kubernetes
from kubernetes.client import ApiException
from loguru import logger
from pydantic import BaseModel

from src.apiserver.repo import Repo
from src.components import config
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
        try:
            ret = srv.k8s_operator_service.v1.create_namespaced_secret(
                config.CONFIG_PROJECT_NAMESPACE,
                kubernetes.client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    data={
                        "auth": base64.b64encode(user.htpasswd.get_secret_value().encode()).decode()
                    },
                    metadata=kubernetes.client.V1ObjectMeta(
                        name=f"{user.username}-basic-auth",
                        namespace=config.CONFIG_PROJECT_NAMESPACE
                    )
                ))
        except ApiException as e:
            if e.reason == 'Conflict':
                logger.warning(f"secret {user.username}-basic-auth already exists")
                return None
            else:
                logger.error(e)
                return e
        if ret is None:
            return RuntimeError("failed to create k8s secret")
        else:
            return None
    return None


async def handle_user_update_event(ev: Union[UserCreateEvent, BaseModel]) -> Optional[Exception]:
    srv = get_root_service()
    user, err = await srv.admin_user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"updating k8s credentials for user {ev.username}")
        try:
            ret = srv.k8s_operator_service.v1.patch_namespaced_secret(
                f"{user.username}-basic-auth",
                config.CONFIG_PROJECT_NAMESPACE,
                kubernetes.client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    data={
                        "auth": base64.b64encode(user.htpasswd.get_secret_value().encode()).decode()
                    },
                    metadata=kubernetes.client.V1ObjectMeta(
                        name=f"{user.username}-basic-auth",
                        namespace=config.CONFIG_PROJECT_NAMESPACE
                    )
                ))
        except ApiException as e:
            if e.reason == 'Not Found':
                logger.warning(f"secret {user.username}-basic-auth not found")
                return None
            else:
                logger.error(e)
                return e
        if ret is None:
            return RuntimeError("failed to update k8s secret")
        else:
            return None
    return None


async def handle_user_delete_event(ev: Union[UserCreateEvent, BaseModel]) -> Optional[Exception]:
    srv = get_root_service()
    user, err = await srv.admin_user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"deleting k8s credentials for user {ev.username}")
        try:
            ret = srv.k8s_operator_service.v1.delete_namespaced_secret(
                f"{user.username}-basic-auth",
                config.CONFIG_PROJECT_NAMESPACE,
            )
        except ApiException as e:
            if e.reason == 'Not Found':
                logger.warning(f"secret {user.username}-basic-auth not found")
                return None
            else:
                logger.error(e)
                return e
        if ret is None:
            return RuntimeError("failed to delete k8s secret")
        else:
            return None
    return None


def get_event_handler(event_type: str) -> Callable[[BaseModel], Coroutine[Any, Any, Optional[Exception]]]:
    if event_type == "user_create_event":
        return handle_user_create_event
    elif event_type == "user_update_event":
        return handle_user_update_event
    elif event_type == "user_delete_event":
        return handle_user_delete_event
    else:
        # TODO: finish
        raise RuntimeError(f"unknown event type {event_type}")
