from pydantic import BaseModel


class UserBaseEvent(BaseModel):
    _type: str = "user_base_event"
    username: str


class UserCreateEvent(UserBaseEvent):
    _type: str = "user_create_event"


class UserUpdateEvent(UserBaseEvent):
    _type: str = "user_update_event"


class UserDeleteEvent(UserBaseEvent):
    _type: str = "user_delete_event"


class TemplateBaseEvent(BaseModel):
    _type: str = "template_base_event"
    template_id: str


class TemplateCreateEvent(TemplateBaseEvent):
    _type: str = "template_create_event"


class TemplateUpdateEvent(TemplateBaseEvent):
    _type = "template_update_event"


class TemplateDeleteEvent(TemplateBaseEvent):
    _type = "template_delete_event"


class PodBaseEvent(BaseModel):
    _type: str = "pod_base_event"
    pod_id: str
    uid: int


class PodCreateEvent(PodBaseEvent):
    _type = "pod_create_event"


class PodUpdateEvent(PodBaseEvent):
    _type = "pod_update_event"


class PodStatusUpdateEvent(PodBaseEvent):
    _type = "pod_status_update_event"
    target_status: str


class PodDeleteEvent(PodBaseEvent):
    _type = "pod_delete_event"
