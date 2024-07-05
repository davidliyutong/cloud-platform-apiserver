from typing import Optional

from pydantic import BaseModel


class QuotaModelV2(BaseModel):
    cpu_m: int
    memory_mb: int
    shared_memory_mb: Optional[int] = None  # none means no shared memory limit
    storage_mb: int
    gpu: Optional[int] = None  # none means no gpu limit
    network_mb: Optional[int] = None  # none means no network limit
    pod_n: int
    max_timeout_sec: Optional[int] = None  # none means no timeout limit
