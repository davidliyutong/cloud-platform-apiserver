import uuid
from typing import List, Optional, Union, Tuple

from pydantic import BaseModel, Field, field_validator

from src.components.datamodels import RBACPolicyModelV2
from src.components.types.common import _ensure_uuid_value, ListRequestBaseModel, ResponseBaseModel


class PolicyListRequest(ListRequestBaseModel):
    pass


class PolicyListResponse(ResponseBaseModel):
    policies: List[RBACPolicyModelV2] = []


class PolicyCreateRequest(BaseModel):
    subject_uuid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    policies: List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]] = Field(default_factory=list)

    @field_validator('subject_uuid')
    def subject_uuid_must_be_valid(cls, v):
        return _ensure_uuid_value(v if v is not None else str(uuid.uuid4()))


class PolicyCreateResponse(ResponseBaseModel):
    policy: RBACPolicyModelV2 = None


class PolicyGetRequest(BaseModel):
    subject_uuid: str = ""


class PolicyGetResponse(ResponseBaseModel):
    policy: RBACPolicyModelV2 = None


class PolicyUpdateRequest(BaseModel):
    subject_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    policies: Optional[List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]]] = None


class PolicyUpdateResponse(ResponseBaseModel):
    pass


class PolicyDeleteRequest(BaseModel):
    subject_uuid: str = ""

    @field_validator('subject_uuid')
    def subject_uuid_must_be_valid(cls, v):
        return _ensure_uuid_value(v)


class PolicyDeleteResponse(ResponseBaseModel):
    pass


class EnforceRequest(BaseModel):
    subject: str = ""
    object: str = ""
    action: str = ""


class EnforceResponse(ResponseBaseModel):
    result: bool = False
