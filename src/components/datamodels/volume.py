import datetime
import uuid
from typing import Optional

from odmantic import Field, Model

from src import CONFIG_BUILD_VERSION
from src.components.datamodels.common import ResourceStatusEnum
from src.components.datamodels.quota import QuotaModelV2


class VolumeModelV2(Model):
    """
    Volume model v2, used to define volume
    """
    model_config = {
        "collection": "volumes",
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.pending, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)
    name: str = Field(primary_field=True, index=True)
    description: str = Field(default="")
    quota: Optional[QuotaModelV2] = Field(default=None)
    owner_username: str = Field()
    owner_uuid: str = Field()  # user uuid
    public: bool = Field(default=False)
