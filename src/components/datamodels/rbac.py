import datetime
import uuid
from typing import List, Tuple, Union

from odmantic import Field, Model
from pydantic import BaseModel

from src import CONFIG_BUILD_VERSION
from src.components.datamodels import policy_collection_name
from src.components.datamodels.common import ResourceStatusEnum


class RBACConfigModelV2(Model):
    """
    RBAC conf model v2, used to define RBAC
    """
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.pending, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    conf: str = Field(default="")


class RBACPolicyModelV2(Model):
    """
    RBAC policy model v2, used to define RBAC
    """
    model_config = {
        "collection": policy_collection_name,
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.committed, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    subject_uuid: str = Field(index=True, primary_field=True, default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(default="")
    description: str = Field(default="")
    policies: List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]] = Field(default_factory=list)


class RBACPolicyExchangeModelV2(BaseModel):
    """
    RBAC policy model v2, used to define RBAC
    """
    policies: List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]] = Field(default_factory=list)
