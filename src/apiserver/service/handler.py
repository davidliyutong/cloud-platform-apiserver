import base64
from typing import Optional, Union

import kubernetes
from kubernetes.client import ApiException

from loguru import logger
from pydantic import BaseModel

from src.components import config
from src.components.events import TemplateCreateEvent, TemplateUpdateEvent, TemplateDeleteEvent, UserCreateEvent, \
    UserUpdateEvent, UserDeleteEvent, PodCreateEvent, PodUpdateEvent, PodDeleteEvent
import src.apiserver.service


async def handle_template_create_event(srv: Optional['src.apiserver.service.RootService'],
                                       ev: Union[TemplateCreateEvent, BaseModel]) -> Optional[Exception]:
    err = await srv.template_service.repo.commit(ev.template_id)
    if err is not None:
        logger.error(f"handle_template_create_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_template_update_event(srv: Optional['src.apiserver.service.RootService'],
                                       ev: Union[TemplateUpdateEvent, BaseModel]) -> Optional[Exception]:
    err = await srv.template_service.repo.commit(ev.template_id)
    if err is not None:
        logger.error(f"handle_template_update_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_template_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                       ev: Union[TemplateDeleteEvent, BaseModel]) -> Optional[Exception]:
    _, err = await srv.template_service.repo.purge(ev.template_id)
    if err is not None:
        logger.error(f"handle_template_delete_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_user_create_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserCreateEvent, BaseModel]) -> Optional[Exception]:
    user, err = await srv.user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"creating k8s credentials for user {ev.username}")
        err = None
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
            if ret is None:
                err = RuntimeError("failed to create k8s secret")
        except ApiException as e:
            if e.reason == 'Conflict':
                logger.warning(f"secret {user.username}-basic-auth already exists")
            else:
                logger.error(e)
                err = e
        if err is None:
            return RuntimeError("failed to create k8s secret")
        else:
            err = await srv.user_service.repo.commit(ev.username)
            if err is not None:
                logger.error(f"handle_user_create_event failed to commit: {err}")
                return err
            else:
                return err
    return None


async def handle_user_update_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserUpdateEvent, BaseModel]) -> Optional[Exception]:
    user, err = await srv.user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"updating k8s credentials for user {ev.username}")
        err = None
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
            if ret is None:
                err = RuntimeError("failed to update k8s secret")
        except ApiException as e:
            if e.reason == 'Not Found':
                logger.warning(f"secret {user.username}-basic-auth not found")
            else:
                logger.error(e)
                err = e
        if err is None:
            return RuntimeError("failed to update k8s secret")
        else:
            err = await srv.user_service.repo.commit(ev.username)
            if err is not None:
                logger.error(f"handle_user_update_event failed to commit: {err}")
                return err
            else:
                return err
    return None


async def handle_user_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserDeleteEvent, BaseModel]) -> Optional[Exception]:
    user, err = await srv.user_service.repo.get(ev.username)
    # TODO: delete user resources from namespace
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"deleting k8s credentials for user {ev.username}")
        err = None
        try:
            ret = srv.k8s_operator_service.v1.delete_namespaced_secret(
                f"{user.username}-basic-auth",
                config.CONFIG_PROJECT_NAMESPACE,
            )
            if ret is None:
                err = RuntimeError("failed to delete k8s secret")
        except ApiException as e:
            if e.reason == 'Not Found':
                logger.warning(f"secret {user.username}-basic-auth not found")
            else:
                logger.error(e)
                err = e

        if err is not None:
            return err
        else:
            _, err = await srv.user_service.repo.purge(ev.username)
            if err is not None:
                logger.error(f"handle_user_delete_event failed to commit: {err}")
                return err
            else:
                return err


async def handle_pod_create_event(srv: Optional['src.apiserver.service.RootService'],
                                  ev: Union[PodCreateEvent, BaseModel]) -> Optional[Exception]:
    # TODO: create pod resources in namespace
    err = await srv.pod_service.repo.commit(ev.pod_id)
    if err is not None:
        logger.error(f"handle_pod_create_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_pod_update_event(srv: Optional['src.apiserver.service.RootService'],
                                  ev: Union[PodUpdateEvent, BaseModel]) -> Optional[Exception]:
    # TODO: update pod resources in namespace
    err = await srv.pod_service.repo.commit(ev.pod_id)
    if err is not None:
        logger.error(f"handle_pod_update_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_pod_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                  ev: Union[PodDeleteEvent, BaseModel]) -> Optional[Exception]:
    # TODO: delete pod resources in namespace
    _, err = await srv.pod_service.repo.purge(ev.pod_id)
    if err is not None:
        logger.error(f"handle_pod_delete_event failed to commit: {err}")
        return err
    else:
        return err
