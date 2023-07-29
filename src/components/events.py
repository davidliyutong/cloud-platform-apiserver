import time

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
