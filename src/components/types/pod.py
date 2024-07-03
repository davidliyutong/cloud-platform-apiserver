from typing import List, Optional, Dict, Any

from pydantic import BaseModel, field_validator, model_validator

from src.components.datamodels import PodModelV1, PodStatusEnum
from src.components.types.common import _ensure_uuid_value, ListRequestBaseModel, ResponseBaseModel


class PodListRequest(ListRequestBaseModel):
    """
    List request for pods
    """
    pass


class PodListResponse(ResponseBaseModel):
    """
    List response for pods
    """
    total_pods: int = 0
    pods: List[PodModelV1] = []


class PodCreateRequest(BaseModel):
    """
    Create request for pods. values is the values for the template (not used).
    timeout_s is the timeout for the pod to run. max is 86400 seconds (24 hours).
    """
    name: str
    description: str
    template_ref: str
    cpu_lim_m_cpu: int
    mem_lim_mb: int
    storage_lim_mb: int
    username: Optional[str] = None
    timeout_s: Optional[int] = None
    values: Optional[Dict[str, Any]] = None

    @field_validator('template_ref')
    def template_ref_must_be_valid(cls, v):
        return _ensure_uuid_value(v)

    @field_validator('cpu_lim_m_cpu')
    def cpu_lim_m_cpu_must_be_valid(cls, v):
        if v < 500:
            raise ValueError('cpu_lim_m_cpu must be greater than 500 mCPU')
        return v

    @field_validator('mem_lim_mb')
    def mem_lim_mb_must_be_valid(cls, v):
        if v < 512:
            raise ValueError('mem_lim_mb must be greater than 512 MB')
        return v

    @field_validator('storage_lim_mb')
    def storage_lim_mb_must_be_valid(cls, v):
        if v < 10240:
            raise ValueError('storage_lim_mb must be greater than 10240 MB')
        return v

    @field_validator('timeout_s')
    def timeout_s_must_be_valid(cls, v):
        if v is None:
            v = 3600
        if v < 0:
            raise ValueError('timeout_s must be positive')
        elif v > 86400:
            raise ValueError('timeout_s must be less than 86400 seconds')
        return v


class PodCreateResponse(ResponseBaseModel):
    """
    Create response for pods
    """
    pod: PodModelV1 = None


class PodGetRequest(BaseModel):
    """
    Get request for pods
    """
    pod_id: str


class PodGetResponse(PodCreateResponse):
    """
    Get response for pods, the same as create response
    """
    pass


class PodUpdateRequest(BaseModel):
    """
    Update request for pods, all fields except pod_id are optional.
    target_status is the target status for the pod to reach. Can be either running or stopped.
    """
    pod_id: Optional[str]
    name: Optional[str] = None
    description: Optional[str] = None
    cpu_lim_m_cpu: Optional[int] = None
    mem_lim_mb: Optional[int] = None
    storage_lim_mb: Optional[int] = None
    username: Optional[str] = None
    user_uuid: Optional[str] = None
    timeout_s: Optional[int] = None
    target_status: Optional[PodStatusEnum] = None
    force: bool = False

    @model_validator(mode="after")
    def validate_request(self):
        if self.timeout_s is not None:
            if self.timeout_s < 0:
                raise ValueError('timeout_s must be positive')
            elif self.timeout_s > 86400 and not self.force:
                raise ValueError('timeout_s must be less than 86400 seconds')

    @field_validator('target_status')
    def target_status_must_be_valid(cls, v):
        if isinstance(v, str):
            v = PodStatusEnum(v)
        if v is not None and v not in PodStatusEnum:
            raise ValueError('target_status must be valid PodStatusEnum')

        if v not in [PodStatusEnum.running, PodStatusEnum.stopped]:
            raise ValueError('target_status must be valid')
        return v

    @field_validator('cpu_lim_m_cpu')
    def cpu_lim_m_cpu_must_be_valid(cls, v):
        return PodCreateRequest.cpu_lim_m_cpu_must_be_valid(v) if v is not None else v

    @field_validator('mem_lim_mb')
    def mem_lim_mb_must_be_valid(cls, v):
        return PodCreateRequest.mem_lim_mb_must_be_valid(v) if v is not None else v

    @field_validator('storage_lim_mb')
    def storage_lim_mb_must_be_valid(cls, v):
        return PodCreateRequest.storage_lim_mb_must_be_valid(v) if v is not None else v


class PodUpdateResponse(PodGetResponse):
    """
    Update response for pods, the same as get response
    """
    pass


class PodDeleteRequest(PodGetRequest):
    """
    Delete request for pods, the same as get request
    """
    pass


class PodDeleteResponse(PodGetResponse):
    """
    Delete response for pods, the same as get response
    """
    pass
