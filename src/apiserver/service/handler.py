"""
This module contains the event handlers for the apiserver service.
"""

import asyncio
import datetime
from typing import Optional, Union

from loguru import logger
from pydantic import BaseModel

from src.components.datamodels import PodStatusEnum, UserStatusEnum, ResourceStatusEnum
from src.components.events import (
    TemplateCreateEvent, TemplateUpdateEvent, TemplateDeleteEvent,
    UserCreateEvent, UserUpdateEvent, UserDeleteEvent,
    PodCreateUpdateEvent, PodDeleteEvent, PodTimeoutEvent,
    UserHeartbeatEvent
)
import src.apiserver.service
from src.components.utils import render_template_str


async def handle_template_create_event(srv: Optional['src.apiserver.service.RootService'],
                                       ev: Union[TemplateCreateEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle template create event
    """

    # just commit the template
    err = await srv.template_service.repo.commit(ev.template_id)
    if err is not None:
        logger.error(f"handle_template_create_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_template_update_event(srv: Optional['src.apiserver.service.RootService'],
                                       ev: Union[TemplateUpdateEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle template update event
    """

    # just commit the template
    err = await srv.template_service.repo.commit(ev.template_id)
    if err is not None:
        logger.error(f"handle_template_update_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_template_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                       ev: Union[TemplateDeleteEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle template delete event
    """

    # just purge the template
    _, err = await srv.template_service.repo.purge(ev.template_id)
    if err is not None:
        logger.error(f"handle_template_delete_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_user_create_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserCreateEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle user create event
    """

    # read user from repo
    user, err = await srv.user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None

    if user is not None:
        logger.info(f"creating k8s credentials for user {ev.username}")

        # create k8s credentials
        err = await srv.k8s_operator_service.create_or_update_user_credentials(
            user.username,
            user.htpasswd.get_secret_value().encode()
        )

        if err is not None:
            logger.error(f"handle_user_create_event failed to create k8s credentials: {err}")
            return err
        else:
            # commit user
            err = await srv.user_service.repo.commit(ev.username)
            if err is not None:
                logger.error(f"handle_user_create_event failed to commit: {err}")
                return err
            else:
                return err
    return None


async def handle_user_update_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserUpdateEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle user update event
    """
    # read user from repo
    user, err = await srv.user_service.repo.get(ev.username)

    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"updating k8s credentials for user {ev.username}")

        # update k8s credentials
        err = await srv.k8s_operator_service.create_or_update_user_credentials(
            user.username,
            user.htpasswd.get_secret_value().encode()
        )

        if err is not None:
            logger.error(f"handle_user_update_event failed to create k8s credentials: {err}")
            return err
        else:
            # commit user
            err = await srv.user_service.repo.commit(ev.username)
            if err is not None:
                logger.error(f"handle_user_update_event failed to commit: {err}")
                return err
            else:
                return err
    return None


async def handle_user_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                   ev: Union[UserDeleteEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle user delete event
    """
    user, err = await srv.user_service.repo.get(ev.username)
    if err is not None:
        logger.warning(err)
        return None
    if user is not None:
        logger.info(f"deleting k8s credentials for user {ev.username}")

        # delete credentials
        err = await srv.k8s_operator_service.delete_user_credential(
            user.username,
        )
        if err is not None:
            logger.error(f"handle_user_delete_event failed to delete k8s credentials: {err}")
            return err

        # delete pods
        logger.info(f"deleting pods for user {ev.username}")
        _, pods, err = await srv.pod_service.repo.list(extra_query_filter={"username": ev.username})  # list pods

        if err is not None:
            logger.error(f"handle_user_delete_event failed to list pods: {err}")
            return err
        for pod in pods:
            if pod.username != ev.username:
                logger.error(f"handle_user_delete_event found pod {pod.pod_id} with wrong username {pod.username}")

            _, err = await srv.pod_service.repo.delete(pod_id=pod.pod_id)  # delete pod

            if err is not None:
                logger.error(f"handle_user_delete_event failed to delete pod {pod.pod_id}: {err}")
                return err

            err = await handle_pod_delete_event(srv, PodDeleteEvent(pod_id=pod.pod_id, username=pod.username))
            if err is not None:
                logger.error(f"handle_user_delete_event failed to delete pod {pod.pod_id}: {err}")
                return err

            _, err = await srv.pod_service.repo.purge(pod_id=pod.pod_id)  # purge pod
            if err is not None:
                logger.error(f"handle_user_delete_event failed to purge pod {pod.pod_id}: {err}")
                return err

        # finally, purge user
        _, err = await srv.user_service.repo.purge(ev.username)
        if err is not None:
            logger.error(f"handle_user_delete_event failed to commit: {err}")
            return err
        else:
            return err


async def handle_pod_create_update_event(srv: Optional['src.apiserver.service.RootService'],
                                         ev: Union[PodCreateUpdateEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle pod create/update event
    """

    # check user's validity
    user, err = await srv.user_service.repo.get(ev.username)
    if any([
        err is not None,
        user.status != UserStatusEnum.active,
        user.resource_status == ResourceStatusEnum.deleted,
    ]):
        logger.error(f"handle_pod_create_update_event failed to get user {ev.username}: {err}")
        return err

    # check if pod is matched
    pod, err = await srv.pod_service.repo.get(ev.pod_id)
    if any([
        err is not None,
        pod.resource_status == ResourceStatusEnum.deleted,
    ]):
        logger.error(f"handle_pod_create_update_event failed to get pod {ev.pod_id}: {err}")
        return err

    # get template
    template, err = await srv.template_service.repo.get(str(pod.template_ref))
    if err is not None:
        logger.error(f"handle_pod_create_update_event failed to get template {pod.template_ref}: {err}")
        return err

    # render template
    kv = pod.values | srv.opt.k8s_config_values | template.values
    template_str, _, err = render_template_str(template.template_str, kv)
    if err is not None:
        logger.error(f"handle_pod_create_update_event failed to parse template {pod.template_ref}: {err}")
        return err

    # create pod on k8s
    err = await srv.k8s_operator_service.create_or_update_pod(pod.pod_id, template_str)
    if err is not None:
        logger.error(f"handle_pod_create_update_event failed to create pod {pod.pod_id}: {err}")
        return err

    # update pod's status
    _now = datetime.datetime.utcnow()
    _, err = await srv.pod_service.repo.update(
        pod_id=pod.pod_id,
        started_at=_now,
        accessed_at=_now,
        current_status=pod.target_status,  # FIXME: might cause trouble
    )
    if err is not None:
        logger.error(f"handle_pod_create_update_event failed to update pod {pod.pod_id}: {err}")
        return err

    # finally purge
    err = await srv.pod_service.repo.commit(ev.pod_id)
    if err is not None:
        logger.error(f"handle_pod_create_update_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_pod_delete_event(srv: Optional['src.apiserver.service.RootService'],
                                  ev: Union[PodDeleteEvent, BaseModel]) -> Optional[Exception]:
    """
    Handle pod delete event
    """

    # delete pod from cluster
    err = await srv.k8s_operator_service.delete_pod(ev.pod_id)
    if err is not None:
        logger.error(f"handle_pod_delete_event failed to delete pod {ev.pod_id}: {err}")
        return err

    # finally purge
    _, err = await srv.pod_service.repo.purge(ev.pod_id)
    if err is not None:
        logger.error(f"handle_pod_delete_event failed to commit: {err}")
        return err
    else:
        return err


async def handle_user_heartbeat_event(srv: Optional['src.apiserver.service.RootService'],
                                      ev: Union[UserHeartbeatEvent, BaseModel]) -> Optional[Exception]:
    err = await srv.heartbeat_service.ping(ev.username)
    if err is not None:
        logger.error(f"handle_user_heartbeat_event failed to list pods: {err}")
        return err

# async def handle_pod_timeout_event(srv: Optional['src.apiserver.service.RootService'],
#                                    ev: Union[PodTimeoutEvent, BaseModel]) -> Optional[Exception]:
#     # TODO: handle pod timeout
#     pass
