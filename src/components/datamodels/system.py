from odmantic import Field, Model
from pydantic import BaseModel

from src import CONFIG_BUILD_VERSION
from .names import system_document_name


class GlobalModel(BaseModel):
    """
    Global status model, used to store global settings in the database
    """
    uid_counter: int = 0
    flag_crashed: bool = False  # record if last run crashed
    version: str = CONFIG_BUILD_VERSION


class SystemStatusModel(BaseModel):
    """
    Global status model, used to store global settings in the database
    """
    flag_crashed: bool = False  # record if last run crashed
    version: str = CONFIG_BUILD_VERSION


class SystemSettingsModel(BaseModel):
    """
    System setting model, used to store global settings in the database
    """
    enable_maintenance: bool = False


class SystemModel(Model):
    """
    System model, used to store global settings in the database
    """
    model_config = {
        "collection": "system",
    }

    name: str = Field(default=system_document_name, key_name="_name")
    status: SystemStatusModel
    settings: SystemSettingsModel
