import datetime
import uuid
from enum import Enum
from typing import Optional, Dict

from odmantic import Field, Model

from src import CONFIG_BUILD_VERSION
from src.components.datamodels import ResourceStatusEnum
from src.components.datamodels.names import group_collection_name
from src.components.datamodels.quota import QuotaModelV2


class GroupEnumInternal(str, Enum):
    """
    Group status enum, used to define group status.
    """
    admin = "admin"
    student = "student"
    professor = "professor"
    guest = "guest"
    default = "default"
    parked = "parked"


class GroupModelV2(Model):
    """
    Group model v2,
    """
    model_config = {
        "collection": group_collection_name,
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.committed, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)
    name: str = Field(primary_field=True, index=True)
    description: str = Field(default="")
    quota: Optional[QuotaModelV2] = Field(default=None)


RESERVED_GROUP_NAMES = [
    GroupEnumInternal.admin.value,
    GroupEnumInternal.student.value,
    GroupEnumInternal.professor.value,
    GroupEnumInternal.guest.value,
    GroupEnumInternal.default.value,
    GroupEnumInternal.parked.value
]


def get_default_groups() -> Dict[str, GroupModelV2]:
    """
    Get default groups
    """

    no_quota = QuotaModelV2(
        cpu_m=0,
        memory_mb=0,
        shared_memory_mb=0,
        storage_mb=0,
        gpu=0,
        network_mb=None,
        pod_n=0,
        max_timeout_sec=0,
    )

    free_quota = QuotaModelV2(
        cpu_m=1000,
        memory_mb=4096,
        shared_memory_mb=0,
        storage_mb=10240,
        gpu=0,
        network_mb=None,
        pod_n=3,
        max_timeout_sec=7200,
    )

    powerful_quota = QuotaModelV2(
        cpu_m=8000,
        memory_mb=16384,
        shared_memory_mb=0,
        storage_mb=51200,
        gpu=0,
        network_mb=None,
        pod_n=10,
        max_timeout_sec=86400 * 2,
    )

    ultimate_quota = QuotaModelV2(
        cpu_m=32000,
        memory_mb=65536,
        shared_memory_mb=None,
        storage_mb=102400,
        gpu=None,
        network_mb=None,
        pod_n=100,
        max_timeout_sec=86400 * 7,
    )

    return {
        GroupEnumInternal.admin.value: GroupModelV2(
            name=GroupEnumInternal.admin.value,
            description="Admin group",
            quota=None
        ),
        GroupEnumInternal.student.value: GroupModelV2(
            name=GroupEnumInternal.student.value,
            description="Student group",
            quota=powerful_quota
        ),
        GroupEnumInternal.professor.value: GroupModelV2(
            name=GroupEnumInternal.professor.value,
            description="Professor group",
            quota=ultimate_quota
        ),
        GroupEnumInternal.guest.value: GroupModelV2(
            name=GroupEnumInternal.guest.value,
            description="Guest group",
            quota=free_quota
        ),
        GroupEnumInternal.default.value: GroupModelV2(
            name=GroupEnumInternal.default.value,
            description="Default group",
            quota=powerful_quota
        ),
        GroupEnumInternal.parked.value: GroupModelV2(
            name=GroupEnumInternal.parked.value,
            description="Parked group",
            quota=no_quota
        ),
    }
