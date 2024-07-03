from enum import Enum

from pydantic import BaseModel

from src import CONFIG_BUILD_VERSION


class GlobalModel(BaseModel):
    """
    Global model, used to store global settings in the database
    """
    uid_counter: int = 0
    flag_crashed: bool = False  # record if last run crashed
    version: str = CONFIG_BUILD_VERSION


class FieldTypeEnum(str, Enum):
    """
    Field type enum, used to define field types
    """
    string = "str"
    integer = "int"
    float = "float"
    boolean = "bool"
    datetime = "datetime"
    list = "list"


class ResourceStatusEnum(str, Enum):
    """
    Resource status enum, used to define resource status. (for error recovery)
    """
    pending = "pending"
    committed = "committed"
    deleted = "deleted"
    finalizing = "finalizing"


# TODO: wait for odmantic support class inheritance
# class BaseModelV2(Model):
#     """
#     Base model v2, used to define base model
#     """
#     version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
#     resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.pending, key_name="_resource_status")
#     created_at: datetime.datetime = Field(
#         default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
#         key_name="_created_at"
#     )
