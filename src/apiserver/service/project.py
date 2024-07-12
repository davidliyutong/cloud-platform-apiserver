"""
Project service
"""

from typing import Tuple, Optional, List, Type, Union

from odmantic import AIOEngine
from sanic import Sanic

from src.components import errors
from src.components.datamodels import public_tag
from src.components.datamodels.project import ProjectModelV2, ResourceStatusEnum
from src.components.types.project import (
    ProjectListRequest, ProjectListByUserRequest,
    ProjectCreateRequest,
    ProjectGetRequest,
    ProjectUpdateRequest,
    ProjectDeleteRequest
)
from src.components.utils.checkers import unmarshal_mongodb_filter
from .common import ServiceInterface
from src.components.datamodels.user import UserModelV2
from src.components.types.rbac import PolicyDeleteRequest, PolicyCreateRequest
from src.components.types.user import UserGetRequest


class ProjectService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self._engine = odm_engine

    async def get(self, app: Sanic, req: ProjectGetRequest) -> Tuple[Optional[ProjectModelV2], Optional[Exception]]:
        """
        Get project.
        """
        res = await self._engine.find_one(ProjectModelV2, ProjectModelV2.project_uuid == req.project_uuid)
        if res is None or res.resource_status in [
            ResourceStatusEnum.deleted,
            ResourceStatusEnum.finalizing,
            ResourceStatusEnum.pending
        ]:
            return None, Exception(errors.user_not_found)

        # TODO: public project hide pod
        return res, None

    async def list(
            self, app: Sanic, req: Union[ProjectListRequest, Type[ProjectListRequest]]
    ) -> Tuple[int, List[ProjectModelV2], Optional[Exception]]:
        """
        List projects.
        """
        query_filter, err = unmarshal_mongodb_filter(req.extra_query_filter)
        if err is not None:
            return 0, [], err
        query_filter = {"$and": [query_filter, {"_resource_status": {"$eq": ResourceStatusEnum.committed.value}}]}

        res = await self._engine.find(ProjectModelV2, query_filter, skip=req.skip, limit=req.limit)
        count = await self._engine.count(ProjectModelV2, query_filter)

        return count, res, None

    async def list_by_user(
            self, app: Sanic, req: Union[ProjectListByUserRequest, Type[ProjectListByUserRequest]]
    ) -> Tuple[int, List[ProjectModelV2], Optional[Exception]]:
        """
        List projects by user.
        """
        if req.username != req.invoke_username:
            user, err = await self.root_service.user_service.get(app, UserGetRequest(username=req.username))
            if err is not None:
                return 0, [], err
            user_uuid = user.uuid
        else:
            user_uuid = req.invoke_user_uuid

        # generate a query filter:
        # 1. owner_uuid == user_uuid
        # 2. project is public
        user_query_filter = {"$and": [
            {"$or": [{"owner_uuid": user_uuid}, {"public": True}]},
            {"_resource_status": {"$eq": ResourceStatusEnum.committed.value}}
        ]}

        res = await self._engine.find(ProjectModelV2, user_query_filter, skip=req.skip, limit=req.limit)
        print(user_query_filter)

        # mask the sensitive information
        for proj in res:
            proj.pod_uuids = []
            proj.volume_uuids = []
            proj.owner_uuid = ""

        count = await self._engine.count(ProjectModelV2, user_query_filter)

        return count, res, None

    async def create(
            self, app: Sanic, req: Union[ProjectCreateRequest, Type[ProjectCreateRequest]],
    ) -> Tuple[Optional[ProjectModelV2], Optional[Exception]]:
        """
        Create a project.
        """
        # check if the owner exists
        owner = await self._engine.find_one(UserModelV2, UserModelV2.uuid == req.owner_uuid)
        if owner is None or owner.resource_status in [ResourceStatusEnum.deleted, ResourceStatusEnum.finalizing]:
            return None, Exception(errors.user_not_found)

        # check if the project name exists in the owner's projects
        project = await self._engine.find_one(
            ProjectModelV2,
            ProjectModelV2.owner_uuid == req.owner_uuid, ProjectModelV2.name == req.name
        )
        if project is not None:
            return None, Exception(errors.project_exists)

        # check against quota
        count = await self._engine.count(ProjectModelV2, ProjectModelV2.owner_uuid == req.owner_uuid)
        if owner.quota:
            # FIXME: user group service to obtain real quota
            if count >= owner.quota.project_count:
                return None, Exception(errors.quota_exceeded)

        async with self._engine.session() as session:
            try:
                project = ProjectModelV2(**req.model_dump())
                await session.save(project)
            except Exception as e:
                return None, e

            # create project policies
            req = PolicyCreateRequest(
                subject_uuid=project.project_uuid,
                name=f"project_{project.project_uuid}_default_policy",
                description=f"default policy for project {project.project_uuid}",
                policies=[
                    ('p', f'user::{owner.username}', f'resources::/projects/{project.project_uuid}/*', x)
                    for x in ['read', 'update', 'delete', 'list', 'create']
                ],
            )
            policy, err = await self.root_service.policy_service.create(app, req)
            if err is not None:
                project.resource_status = ResourceStatusEnum.pending
                await session.save(project)
                return None, err

        return project, None

    async def update(
            self, app: Sanic, req: Union[ProjectUpdateRequest, Type[ProjectUpdateRequest]]
    ) -> Tuple[Optional[ProjectModelV2], Optional[Exception]]:
        """
        Update a project.
        """
        project = await self._engine.find_one(
            ProjectModelV2, ProjectModelV2.project_uuid == req.project_uuid
        )

        if project is None:
            return None, Exception(errors.project_not_found)

        # selectively update fields
        project.name = req.name if req.name is not None else project.name
        project.description = req.description if req.description is not None else project.description
        project.public = req.public if req.public is not None else project.public
        project.owner_uuid = req.owner_uuid if req.owner_uuid is not None else project.owner_uuid

        # check if project name is reserved
        project = ProjectModelV2(**project.model_dump())

        project.resource_status = ResourceStatusEnum.committed
        try:
            await self._engine.save(project)
        except Exception as e:
            return None, e

        return project, None

    async def delete(
            self, app: Sanic, req: Union[ProjectDeleteRequest, Type[ProjectDeleteRequest]]
    ) -> Tuple[Optional[ProjectModelV2], Optional[Exception]]:
        """
        Delete a project. This is a soft delete.
        """
        project = await self._engine.find_one(
            ProjectModelV2, ProjectModelV2.project_uuid == req.project_uuid
        )

        if project is None:
            return None, Exception(errors.project_not_found)

        # cannot delete owner's named project
        user, err = await self.root_service.user_service.get_by_uuid(app, project.owner_uuid)
        if err is not None:
            return None, err
        if user.username == project.name:
            return None, Exception(errors.project_cannot_be_deleted)

        try:
            async with self._engine.session() as session:
                project.resource_status = ResourceStatusEnum.deleted
                await session.save(project)

                # delete user policies
                req = PolicyDeleteRequest(subject_uuid=project.project_uuid)
                await self.root_service.policy_service.delete(app, req)

                project.resource_status = ResourceStatusEnum.finalizing
                await session.save(project)

        except Exception as e:
            return None, e

        # TODO: trigger project delete event
        return project, None

    async def purge(self, project_uuid: str) -> Optional[Exception]:
        """
        Purge a user
        """
        user = await self._engine.find_one(ProjectModelV2, ProjectModelV2.project_uuid == project_uuid)
        if user is None:
            return errors.user_not_found
        else:
            try:
                await self._engine.delete(user)
                return None
            except Exception as e:
                return e
