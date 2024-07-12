import datetime
import re
import uuid
from typing import List

from odmantic import Field, Model
from pydantic import field_validator

from src import CONFIG_BUILD_VERSION
from src.components.datamodels.names import project_collection_name
from src.components.datamodels.common import ResourceStatusEnum


class ProjectModelV2(Model):
    """
    Project model v2, project contains pods and volumes
    """
    model_config = {
        "collection": project_collection_name,
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.committed, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    project_uuid: str = Field(index=True, primary_field=True, default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(default="")
    description: str = Field(default="")

    public: bool = Field(default=False)
    owner_uuid: str = Field(default="")

    pod_uuids: List[str] = Field(default_factory=list)
    volume_uuids: List[str] = Field(default_factory=list)

    @field_validator("name")
    def name_must_be_valid(cls, v):
        pattern = '^[0-9a-zA-Z\-_]*$'
        if v.startswith('_') or v.startswith('-') or v.startswith('.'):
            raise ValueError("username must not start with _, -, or .")
        if not re.match(pattern, v):
            raise ValueError("username must be alphanumeric")
        return v
