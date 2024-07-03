"""
Data models for the project
"""
from sanic_ext import openapi

from .names import (
    database_name,
    system_collection_name,
    user_collection_name,
    pod_collection_name,
    template_collection_name,
    volume_collection_name,
    group_collection_name,
    policy_collection_name
)

from .common import FieldTypeEnum, ResourceStatusEnum
from .pod import PodModelV1, PodStatusEnum
from .quota import QuotaModelV2
from .rbac import RBACPolicyModelV2, RBACConfigModelV2
from .system import GlobalModel, SystemModel, SystemStatusModel, SystemSettingsModel
from .template import TemplateModel
from .user import UserRoleEnum, UserStatusEnum, UserModelV2

# attention: registrate components
openapi.component(FieldTypeEnum)
openapi.component(ResourceStatusEnum)
openapi.component(PodModelV1)
openapi.component(PodStatusEnum)
openapi.component(QuotaModelV2)
openapi.component(RBACPolicyModelV2)
# openapi.component(RBACConfigModelV2) # not used
# openapi.component(GlobalModel) # not used
# openapi.component(SystemModel) # not used
openapi.component(TemplateModel)
openapi.component(UserRoleEnum)
openapi.component(UserStatusEnum)
openapi.component(UserModelV2)