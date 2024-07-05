"""
Data models for the project
"""
from sanic_ext import openapi

from .common import FieldTypeEnum, ResourceStatusEnum


def _register_components():
    # attention: registrate components
    openapi.component(FieldTypeEnum)
    openapi.component(ResourceStatusEnum)

    from .group import GroupEnumInternal, GroupModelV2
    openapi.component(GroupEnumInternal)
    openapi.component(GroupModelV2)

    from .pod import PodModelV1, PodStatusEnum
    openapi.component(PodModelV1)
    openapi.component(PodStatusEnum)

    from .project import ProjectModelV2
    openapi.component(ProjectModelV2)

    from .quota import QuotaModelV2
    openapi.component(QuotaModelV2)

    from .rbac import RBACPolicyModelV2
    openapi.component(RBACPolicyModelV2)

    from .system import GlobalModel, SystemModel, SystemStatusModel, SystemSettingsModel

    from .template import TemplateModel, PodTemplateModelV2, VolumeTemplateModelV2
    openapi.component(TemplateModel)
    openapi.component(PodTemplateModelV2)
    openapi.component(VolumeTemplateModelV2)

    from .user import UserRoleEnum, UserStatusEnum, UserModelV2
    openapi.component(UserRoleEnum)
    openapi.component(UserStatusEnum)
    openapi.component(UserModelV2)

    from .volume import VolumeModelV2
    openapi.component(VolumeModelV2)


_register_components()
