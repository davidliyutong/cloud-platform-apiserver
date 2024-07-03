import uuid
from typing import Optional

from pydantic import BaseModel


def _ensure_uuid_value(v):
    if v == "" or v is None:
        raise ValueError("uuid cannot be empty")
    try:
        _ = uuid.UUID(v)
    except ValueError as e:
        raise e
    return v


def _ensure_non_empty_value(v, field_name=""):
    if v == "":
        raise ValueError(f"field[{field_name}] cannot be empty")
    return v


class ListRequestBaseModel(BaseModel):
    """
    Base model for list request
    """
    skip: int = 0  # 0 means start from the beginning
    limit: Optional[int] = None  # None means end at the end
    extra_query_filter: str = ''  # mongodb query filter in json format


class ResponseBaseModel(BaseModel):
    """
    Base model for response
    """
    description: str = ""  # description of the response
    status: int  # status code of the response
    message: str  # message of the response


class OIDCStatusResponse(BaseModel):
    name: str
    path: str
