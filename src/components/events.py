"""
This module contains the event models and the event deserialization function.

A event must contain a `type` field, which is a string that indicates the type of the event.
"""

import json
from typing import Optional, Tuple, Union

from pydantic import BaseModel


class UserBaseEvent(BaseModel):
    type: str = "user_base_event"
    username: str


class UserCreateEvent(UserBaseEvent):
    type: str = "user_create_event"


class UserUpdateEvent(UserBaseEvent):
    type: str = "user_update_event"


class UserDeleteEvent(UserBaseEvent):
    type: str = "user_delete_event"


class TemplateBaseEvent(BaseModel):
    type: str = "template_base_event"
    template_id: str


class TemplateCreateEvent(TemplateBaseEvent):
    type: str = "template_create_event"


class TemplateUpdateEvent(TemplateBaseEvent):
    type: str = "template_update_event"


class TemplateDeleteEvent(TemplateBaseEvent):
    type: str = "template_delete_event"


class PodBaseEvent(BaseModel):
    type: str = "pod_base_event"
    pod_id: str
    username: str


class PodCreateUpdateEvent(PodBaseEvent):
    type: str = "pod_create_update_event"


class PodDeleteEvent(PodBaseEvent):
    type: str = "pod_delete_event"


class PodTimeoutEvent(PodBaseEvent):
    type: str = "pod_timeout_event"


class UserHeartbeatEvent(BaseModel):
    type: str = "user_heartbeat_event"
    username: str


def event_deserialize(payload: Union[bytes, str]) -> Tuple[Optional[BaseModel], Optional[Exception]]:
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError as e:
        return None, e

    if payload['type'] == 'user_create_event':
        return UserCreateEvent(**payload), None
    elif payload['type'] == 'user_update_event':
        return UserUpdateEvent(**payload), None
    elif payload['type'] == 'user_delete_event':
        return UserDeleteEvent(**payload), None
    elif payload['type'] == 'template_create_event':
        return TemplateCreateEvent(**payload), None
    elif payload['type'] == 'template_update_event':
        return TemplateUpdateEvent(**payload), None
    elif payload['type'] == 'template_delete_event':
        return TemplateDeleteEvent(**payload), None
    elif payload['type'] == 'pod_create_update_event':
        return PodCreateUpdateEvent(**payload), None
    elif payload['type'] == 'pod_delete_event':
        return PodDeleteEvent(**payload), None
    elif payload['type'] == 'pod_timeout_event':
        return PodTimeoutEvent(**payload), None
    elif payload['type'] == 'user_heartbeat_event':
        return UserHeartbeatEvent(**payload), None

    return None, Exception(f"unknown event type: {payload['type']}")
