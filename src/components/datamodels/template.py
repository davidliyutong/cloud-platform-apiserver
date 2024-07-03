import datetime
import uuid
from enum import Enum
from typing import Optional, Dict, Any, Self

from odmantic import Field, Model
from pydantic import BaseModel, UUID4, field_validator, field_serializer

from src import CONFIG_BUILD_VERSION
from src.components import config as config
from . import template_collection_name
from .common import ResourceStatusEnum, FieldTypeEnum


class TemplateModel(BaseModel):
    """
    Template model, used to define template
    """
    version: str
    resource_status: ResourceStatusEnum = ResourceStatusEnum.pending
    template_id: UUID4
    name: str
    description: str
    image_ref: str
    template_str: str
    fields: Optional[Dict[str, FieldTypeEnum]]  # not used
    defaults: Optional[Dict[str, Any]]  # not used

    @field_validator("version")
    def version_must_be_valid(cls, v):
        if v is None or v == "":
            v = CONFIG_BUILD_VERSION
        return v

    @field_validator("template_id")
    def uuid_must_be_valid(cls, v):
        if v is None:
            v = uuid.uuid4()
        if not isinstance(v, uuid.UUID):
            v = uuid.UUID(v)
        return v

    @field_serializer('template_id')
    def serialize_uuid(self, v: uuid.UUID, _info):
        return str(v)

    @field_serializer('fields')
    def serialize_fields(self, v: Dict[str, FieldTypeEnum], _info):
        if v is not None:
            return {
                _k: str(_v) for _k, _v in v.items()
            }
        else:
            return None

    @classmethod
    def new(cls,
            name: str,
            description: str,
            image_ref: str,
            template_str: str,
            fields: Optional[Dict[str, Any]],
            defaults: Optional[Dict[str, Any]]):
        return cls(
            version=CONFIG_BUILD_VERSION,
            template_id=uuid.uuid4(),
            name=name,
            description=description,
            image_ref=image_ref,
            template_str=template_str,
            fields=fields,
            defaults=defaults,
        )

    # example values to test if template is valid
    # attention: strong dependency on project design
    __EXAMPLE_VALUES__ = {
        "POD_LABEL": config.CONFIG_K8S_POD_LABEL_FMT.format("test_id"),
        "POD_ID": "test_id",
        "POD_CPU_LIM": "2000m",
        "POD_MEM_LIM": "4096Mi",
        "POD_STORAGE_LIM": "10Mi",
        "POD_REPLICAS": "1",
        # there is no POD_USERNAME, POD_AUTH
        "TEMPLATE_IMAGE_REF": "davidliyutong/code-server-speit:latest",
    }

    def verify(self) -> bool:
        from src.components.utils.templating import render_template_str
        template_str, used_keys, _ = render_template_str(self.template_str, self.__EXAMPLE_VALUES__)
        return len(set(used_keys)) == len(self.__EXAMPLE_VALUES__)

    @property
    def values(self):
        return {
            'TEMPLATE_IMAGE_REF': self.image_ref,
        }

    @classmethod
    def upgrade(cls, d: Dict[str, Any]) -> Self:
        res = cls(**d)
        res.version = CONFIG_BUILD_VERSION
        return res


class TemplateTypeEnum(str, Enum):
    """
    Template type enum
    """
    standard = "standard"
    custom = "custom"


class TemplateModelV2(Model):
    """
    Template model, used to define template
    """
    model_config = {
        "collection": template_collection_name,
    }
    version: str = Field(default=CONFIG_BUILD_VERSION, key_name="_version")
    resource_status: ResourceStatusEnum = Field(default=ResourceStatusEnum.committed, key_name="_resource_status")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        key_name="_created_at"
    )

    template_uuid: str = Field(index=True, primary_field=True, default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(default="")
    description: str = Field(default="")

    template_type: TemplateTypeEnum = Field(default=TemplateTypeEnum.standard)
    image_ref: str = Field()
    template_str: Optional[str] = Field(default=None)

    # portMapping
    # mountPoints
    def verify(self) -> bool:
        if self.template_type == TemplateTypeEnum.standard:
            return True
        elif self.template_type == TemplateTypeEnum.custom:
            # TODO: verify template_str has correct format
            return self.template_str is not None