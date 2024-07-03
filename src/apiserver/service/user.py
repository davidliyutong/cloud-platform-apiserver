"""
User service
"""
from typing import Type, Optional, Tuple, List, Union
from pydantic import SecretStr

from odmantic import AIOEngine
from sanic import Sanic

from src.components import errors
from src.components.datamodels import UserModelV2, ResourceStatusEnum
from src.components.datamodels.user import RESERVED_USERNAMES
from src.components.utils.checkers import unmarshal_mongodb_filter
from src.components.utils.security import get_hashed_text

from .common import ServiceInterface
from src.components.types.rbac import PolicyCreateRequest, PolicyDeleteRequest
from src.components.types.user import UserListRequest, UserCreateRequest, UserGetRequest, UserUpdateRequest, \
    UserDeleteRequest


class UserService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self._engine = odm_engine

    async def commit(self, username: str) -> Optional[Exception]:
        """
        Commit a user.
        """
        with self._engine.session() as session:
            user = await session.find_one(UserModelV2, UserModelV2.username == username)
            if user is None:
                return errors.user_not_found
            else:
                user.resource_status = ResourceStatusEnum.committed
                try:
                    await session.save(user)
                    return None
                except Exception as e:
                    return e

    async def get(self,
                  app: Sanic,
                  req: UserGetRequest) -> Tuple[Optional[UserModelV2], Optional[Exception]]:
        """
        Get user.
        """
        res = await self._engine.find_one(
            UserModelV2,
            UserModelV2.username == req.username  # and UserModelV2.resource_status != ResourceStatusEnum.deleted
        )
        if res is None or res.resource_status in [ResourceStatusEnum.deleted, ResourceStatusEnum.finalizing]:
            return None, Exception(errors.user_not_found)

        return res, None

    async def list(
            self,
            app: Sanic,
            req: Union[UserListRequest, Type[UserListRequest]]
    ) -> Tuple[int, List[UserModelV2], Optional[Exception]]:
        """
        List users.
        """
        query_filter, err = unmarshal_mongodb_filter(req.extra_query_filter)
        if err is not None:
            return 0, [], err

        res = await self._engine.find(UserModelV2, query_filter, skip=req.skip, limit=req.limit)
        count = await self._engine.count(UserModelV2, query_filter)
        return count, res, None

    async def create(
            self,
            app: Sanic,
            req: Union[UserCreateRequest, Type[UserCreateRequest]],
            registration: bool = False
    ) -> Tuple[Optional[UserModelV2], Optional[Exception]]:
        """
        Create a user.
        """
        user = await self._engine.find_one(UserModelV2, UserModelV2.username == req.username)
        if user is not None:
            return None, Exception(errors.user_exists)

        # if the user is registering, check if the username is in the reserved list
        if registration:
            if req.username in RESERVED_USERNAMES:
                return None, Exception(errors.username_illegal)

        async with self._engine.session() as session:
            try:
                req.password = get_hashed_text(req.password) if req.password else SecretStr("")
                user = UserModelV2(**req.dict())
                await session.save(user)
            except Exception as e:
                return None, e

            try:
                user_default_policy = PolicyCreateRequest(
                    subject_uuid=user.uuid,
                    name=f"user_{user.username}_default_policy",
                    description=f"default policy for user {user.username}",
                    policies=[
                        ('g', f'user::{user.username}', 'role::user'),
                        ('p', f'user::{user.username}', f'resources::/users/{user.username}', 'read'),
                        ('p', f'user::{user.username}', f'resources::/users/{user.username}', 'list'),
                        ('p', f'user::{user.username}', f'resources::/users/{user.username}', 'update'),
                        ('p', f'user::{user.username}', f'resources::/users/{user.username}', 'delete'),
                        ('p', f'user::{user.username}', f'resources::/projects/.by_username/{user.username}/*', 'read'),
                        ('p', f'user::{user.username}', f'resources::/projects/.by_username/{user.username}/*', 'list'),
                        ('p', f'user::{user.username}', f'resources::/projects/.by_username/{user.username}/*',
                         'update'),
                        ('p', f'user::{user.username}', f'resources::/projects/.by_username/{user.username}/*',
                         'delete'),
                        ('p', f'user::{user.username}', f'resources::/volumes/.by_username/{user.username}/*', 'read'),
                        ('p', f'user::{user.username}', f'resources::/volumes/.by_username/{user.username}/*', 'list'),
                        (
                            'p', f'user::{user.username}', f'resources::/volumes/.by_username/{user.username}/*',
                            'update'),
                        (
                            'p', f'user::{user.username}', f'resources::/volumes/.by_username/{user.username}/*',
                            'delete'),
                    ]
                )
                await self.root_service.policy_service.create(app, user_default_policy)
            except Exception as e:
                return None, e

            # TODO: create associated project
            return user, None

    async def update(
            self,
            app: Sanic,
            req: Union[UserUpdateRequest, Type[UserUpdateRequest]]
    ) -> Tuple[Optional[UserModelV2], Optional[Exception]]:
        """
        Update a user.
        """
        user = await self._engine.find_one(UserModelV2, UserModelV2.username == req.username)
        if user is None:
            return None, Exception(errors.user_not_found)

        # selectively update fields
        user.email = req.email if req.email is not None else user.email
        user.public_keys = req.public_keys if req.public_keys is not None else user.public_keys
        user.extra_info = req.extra_info if req.extra_info is not None else user.extra_info

        if req.update_password:
            if req.old_password is None:
                user.password = get_hashed_text(req.new_password) if req.new_password is not None else user.password
            else:
                if not user.challenge_password(req.old_password):
                    return None, Exception(errors.wrong_password)

                if user.otp_enabled:
                    # check if otp code is provided
                    if req.otp_code is None:
                        return None, Exception(errors.otp_code_required)

                    # check if otp code is correct
                    if not user.challenge_otp_code(req.otp_code):
                        return None, Exception(errors.otp_code_required)

                user.password = get_hashed_text(req.new_password) if req.new_password is not None else user.password

        if req.update_quota:
            user.quota = req.quota if req.quota is not None else user.quota

        if req.update_group:
            user.group = req.group if req.group is not None else user.group

        if req.update_status:
            user.status = req.status if req.status is not None else user.status

        if req.update_otp:
            # check if user has password
            if user.password is None or user.password.get_secret_value() == "":
                return None, Exception(errors.otp_password_required)
            # check if otp is enabled
            if user.otp_enabled:
                # check if otp code is provided
                if req.otp_code is None:
                    return None, Exception(errors.otp_code_required)

                # check if otp code is correct
                if not user.challenge_otp_code(req.otp_code):
                    return None, Exception(errors.otp_code_wrong)
            # update otp secret
            user.otp_secret = req.otp_secret if req.otp_secret is not None else user.otp_secret

        if req.update_otp_status:
            if user.challenge_otp_code(req.otp_code):
                user.otp_enabled = req.otp_enabled
            else:
                return None, Exception(errors.otp_code_wrong)

        user.resource_status = ResourceStatusEnum.committed
        try:
            await self._engine.save(user)
        except Exception as e:
            return None, e

        return user, None

    async def delete(
            self,
            app: Sanic,
            req: Union[UserDeleteRequest, Type[UserDeleteRequest]]
    ) -> Tuple[Optional[UserModelV2], Optional[Exception]]:
        """
        Delete a user.
        """
        user = await self._engine.find_one(UserModelV2, UserModelV2.username == req.username)
        if user is None or user.resource_status == ResourceStatusEnum.deleted:
            return None, Exception(errors.user_not_found)

        if req.password is not None:
            if not user.challenge_password(req.password):
                return None, Exception(errors.wrong_password)

        if user.otp_enabled:
            # check if otp code is provided
            if req.otp_code is None:
                return None, Exception(errors.otp_code_required)

            # check if otp code is correct
            if not user.challenge_otp_code(req.otp_code):
                return None, Exception(errors.otp_code_wrong)

        # mark user as deleted
        async with self._engine.session() as session:
            user.resource_status = ResourceStatusEnum.deleted
            try:
                await session.save(user)
            except Exception as e:
                return None, e

            # delete user policies
            try:
                req = PolicyDeleteRequest(subject_uuid=user.uuid)
                await self.root_service.policy_service.delete(app, req)
            except Exception as e:
                return None, e

            # TODO: delete associated project
            # TODO: trigger user delete event
            return user, None

    async def purge(self, username: str) -> Optional[Exception]:
        """
        Purge a user
        """
        user = await self._engine.find_one(UserModelV2, UserModelV2.username == username)
        if user is None:
            return errors.user_not_found
        else:
            try:
                await self._engine.delete(user)
                return None
            except Exception as e:
                return e
