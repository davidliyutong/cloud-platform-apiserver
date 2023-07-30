import json
from typing import Optional, Tuple, Union

from pydantic import BaseModel, field_validator


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
    uid: int


class PodCreateEvent(PodBaseEvent):
    type: str = "pod_create_event"


class PodUpdateEvent(PodBaseEvent):
    type: str = "pod_update_event"


class PodStatusUpdateEvent(PodBaseEvent):
    type: str = "pod_status_update_event"
    target_status: str


class PodDeleteEvent(PodBaseEvent):
    type: str = "pod_delete_event"


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
    elif payload['type'] == 'pod_create_event':
        return PodCreateEvent(**payload), None
    elif payload['type'] == 'pod_update_event':
        return PodUpdateEvent(**payload), None
    elif payload['type'] == 'pod_status_update_event':
        return PodStatusUpdateEvent(**payload), None
