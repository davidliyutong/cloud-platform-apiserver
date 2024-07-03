from typing import List, Optional, Dict, Any

from pydantic import BaseModel

from src.components.datamodels.template import TemplateTypeEnum, TemplateModelV2
from src.components.types.common import ListRequestBaseModel, ResponseBaseModel


class TemplateListRequest(ListRequestBaseModel):
    """
    List request for templates
    """
    pass


class TemplateListResponse(ResponseBaseModel):
    """
    List response for templates
    """
    total_templates: int = 0
    templates: List[TemplateModelV2] = []


class TemplateCreateRequest(BaseModel):
    """
    Create request for templates.
    fields and defaults are optional and not yet used.
    """
    name: str
    description: str
    template_type: TemplateTypeEnum = TemplateTypeEnum.standard
    image_ref: str
    template_str: Optional[str]


class TemplateCreateResponse(ResponseBaseModel):
    """
    Create response for templates
    """
    template: TemplateModelV2 = None


class TemplateGetRequest(BaseModel):
    """
    Get request for templates
    """
    template_uuid: str


class TemplateGetResponse(TemplateCreateResponse):
    """
    Get response for templates, the same as create response
    """
    pass


class TemplateUpdateRequest(BaseModel):
    """
    Update request for templates, all fields except template_id are optional.
    """
    template_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None

    template_type: Optional[TemplateTypeEnum] = None
    image_ref: Optional[str] = None
    template_str: Optional[str] = None


class TemplateUpdateResponse(TemplateGetResponse):
    """
    Update response for templates, the same as get response
    """
    pass


class TemplateDeleteRequest(TemplateGetRequest):
    """
    Delete request for templates, the same as get request
    """
    pass


class TemplateDeleteResponse(TemplateGetResponse):
    """
    Delete response for templates, the same as get response
    """
    pass
