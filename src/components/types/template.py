from typing import List, Optional, Dict, Any

from pydantic import BaseModel

from src.components.datamodels.template import (
    PodTemplateTypeEnum, PodTemplateModelV2,
    VolumeTemplateTypeEnum, VolumeTemplateModelV2, VolumeMountTypeEnum
)
from src.components.types.common import ListRequestBaseModel, ResponseBaseModel


class PodTemplateListRequest(ListRequestBaseModel):
    """
    List request for templates
    """
    tag: str = None


class PodTemplateListResponse(ResponseBaseModel):
    """
    List response for templates
    """
    total_templates: int = 0
    templates: List[PodTemplateModelV2] = []


class PodTemplateCreateRequest(BaseModel):
    """
    Create request for templates.
    fields and defaults are optional and not yet used.
    """
    name: str
    description: str
    template_type: PodTemplateTypeEnum = PodTemplateTypeEnum.standard
    image_ref: str
    template_str: Optional[str]


class PodTemplateCreateResponse(ResponseBaseModel):
    """
    Create response for templates
    """
    template: PodTemplateModelV2 = None


class PodTemplateGetRequest(BaseModel):
    """
    Get request for templates
    """
    template_uuid: str


class PodTemplateGetResponse(PodTemplateCreateResponse):
    """
    Get response for templates, the same as create response
    """
    pass


class PodTemplateUpdateRequest(BaseModel):
    """
    Update request for templates, all fields except template_id are optional.
    """
    template_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None

    template_type: Optional[PodTemplateTypeEnum] = None
    image_ref: Optional[str] = None
    template_str: Optional[str] = None


class PodTemplateUpdateResponse(PodTemplateGetResponse):
    """
    Update response for templates, the same as get response
    """
    pass


class PodTemplateDeleteRequest(PodTemplateGetRequest):
    """
    Delete request for templates, the same as get request
    """
    pass


class PodTemplateDeleteResponse(PodTemplateGetResponse):
    """
    Delete response for templates, the same as get response
    """
    pass


class VolumeTemplateListRequest(ListRequestBaseModel):
    """
    List request for volume templates
    """
    tag: str = None


class VolumeTemplateListResponse(ResponseBaseModel):
    """
    List response for volume templates
    """
    total_templates: int = 0
    templates: List[VolumeTemplateModelV2] = []


class VolumeTemplateCreateRequest(BaseModel):
    """
    Create request for volume templates.
    """
    name: str
    description: str
    template_type: VolumeTemplateTypeEnum = VolumeTemplateTypeEnum.standard
    storage_class: str
    max_size_mb: int = 10240
    mount_type: VolumeMountTypeEnum = VolumeMountTypeEnum.read_write_once
    template_str: Optional[str]


class VolumeTemplateCreateResponse(ResponseBaseModel):
    """
    Create response for volume templates
    """
    template: VolumeTemplateModelV2 = None


class VolumeTemplateGetRequest(BaseModel):
    """
    Get request for volume templates
    """
    template_uuid: str


class VolumeTemplateGetResponse(VolumeTemplateCreateResponse):
    """
    Get response for volume templates, the same as create response
    """
    pass


class VolumeTemplateUpdateRequest(BaseModel):
    """
    Update request for volume templates, all fields except template_uuid are optional.
    """
    template_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[VolumeTemplateTypeEnum] = None
    storage_class: Optional[str] = None
    max_size_mb: Optional[int] = None
    mount_type: Optional[VolumeMountTypeEnum] = None
    template_str: Optional[str] = None


class VolumeTemplateUpdateResponse(VolumeTemplateGetResponse):
    """
    Update response for volume templates, the same as get response
    """
    pass


class VolumeTemplateDeleteRequest(VolumeTemplateGetRequest):
    """
    Delete request for volume templates, the same as get request
    """
    pass


class VolumeTemplateDeleteResponse(VolumeTemplateGetResponse):
    """
    Delete response for volume templates, the same as get response
    """
    pass
