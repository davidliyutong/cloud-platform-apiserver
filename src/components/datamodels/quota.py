from typing import Optional

from pydantic import BaseModel


class QuotaModelV2(BaseModel):
    cpu_m: int
    memory_mb: int
    storage_mb: int
    gpu: int  # attention: not used
    network_mb: int  # attention: not used
    pod_n: int
    max_timeout_sec: Optional[int] = None
