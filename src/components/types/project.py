from typing import List, Optional

from pydantic import BaseModel

from src.components.datamodels.project import ProjectModelV2
from src.components.types.common import ListRequestBaseModel, ResponseBaseModel


class ProjectListRequest(ListRequestBaseModel):
    """
    List request for projects
    """


class ProjectListByUserRequest(ListRequestBaseModel):
    """
    List request for projects
    """
    username: str
    invoke_user_uuid: str
    invoke_username: str
    pass


class ProjectListResponse(ResponseBaseModel):
    """
    List response for projects
    """
    total_projects: int = 0
    projects: List[ProjectModelV2] = []


class ProjectCreateRequest(BaseModel):
    """
    Create request for projects.
    """
    name: str = ""
    description: str = ""
    public: bool = False
    owner_uuid: str = None


class ProjectCreateResponse(ResponseBaseModel):
    """
    Create response for projects
    """
    project: ProjectModelV2 = None


class ProjectGetRequest(BaseModel):
    """
    Get request for projects
    """
    project_uuid: str
    tag: str = None


class ProjectGetResponse(ProjectCreateResponse):
    """
    Get response for projects, the same as create response
    """
    pass


class ProjectUpdateRequest(BaseModel):
    """
    Update request for projects, all fields except project_uuid are optional.
    """
    project_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    public: Optional[bool] = None
    owner_uuid: Optional[str] = None


class ProjectUpdateResponse(ProjectGetResponse):
    """
    Update response for projects, the same as get response
    """
    pass


class ProjectDeleteRequest(ProjectGetRequest):
    """
    Delete request for projects, the same as get request
    """
    force: bool = False


class ProjectDeleteResponse(ProjectGetResponse):
    """
    Delete response for projects, the same as get response
    """
    pass
