import http
from typing import Tuple, Optional, List, Type, Union

import aiohttp
from loguru import logger
from odmantic import AIOEngine

from src.apiserver.service import ServiceInterface
from src.components import errors
from src.components.datamodels import RBACPolicyModelV2, ResourceStatusEnum
from src.components.types.rbac import PolicyListRequest, PolicyCreateRequest, PolicyGetRequest, PolicyUpdateRequest, \
    PolicyDeleteRequest
from src.components.utils.checkers import unmarshal_mongodb_filter

import src.clients.rbac_client.clpl_rbacserver_client as rbac_client

# Enter a context with an instance of the API client
RBAC_DEFAULT_ENDPOINT = "http://127.0.0.1:8081"  # TODO: Currently hardcoded, should be configurable
RBAC_DEFAULT_POLICY_NAME = "default"


class PolicyService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self._engine = odm_engine
        self._configuration = rbac_client.Configuration(
            host=RBAC_DEFAULT_ENDPOINT
        )

    async def get(self, app, req: PolicyGetRequest) -> Tuple[Optional[RBACPolicyModelV2], Optional[Exception]]:
        """
        Get Policy.
        """
        res = await self._engine.find_one(RBACPolicyModelV2, RBACPolicyModelV2.subject_uuid == req.subject_uuid)
        return res, None if res is not None else Exception(errors.policy_not_found)

    async def list(
            self,
            app,
            req: Union[PolicyListRequest, Type[PolicyListRequest]]
    ) -> Tuple[int, List[RBACPolicyModelV2], Optional[Exception]]:
        """
        List Policy.
        """
        query_filter, err = unmarshal_mongodb_filter(req.extra_query_filter)

        # set default query_filter
        if query_filter is None or len(query_filter) == 0:
            query_filter = {"name": {"$not": {"$eq": "default"}}}

        if err is not None:
            return 0, [], err
        res = await self._engine.find(RBACPolicyModelV2, query_filter, skip=req.skip, limit=req.limit)
        count = await self._engine.count(RBACPolicyModelV2, query_filter)
        return count, res, None

    async def create(
            self,
            app,
            req: Union[PolicyCreateRequest, Type[PolicyCreateRequest]]
    ) -> Tuple[Optional[RBACPolicyModelV2], Optional[Exception]]:
        """
        Create a Policy.
        """
        try:
            policy = RBACPolicyModelV2(**req.dict())
            await self._engine.save(policy)
        except Exception as e:
            return None, e

        await self._notify_policy_add(policy)
        return policy, None

    async def update(
            self,
            app,
            req: Union[PolicyUpdateRequest, Type[PolicyUpdateRequest]]
    ) -> Tuple[Optional[RBACPolicyModelV2], Optional[Exception]]:
        """
        Update a Policy.
        """
        policy = await self._engine.find_one(RBACPolicyModelV2, RBACPolicyModelV2.subject_uuid == req.subject_uuid)
        if policy is None:
            return None, Exception(errors.user_not_found)

        # default policy cannot be deleted
        if policy.name == RBAC_DEFAULT_POLICY_NAME:
            return None, Exception(errors.policy_cannot_be_modified)

        # selectively update fields
        policy.name = req.name if req.name is not None else policy.name
        policy.description = req.description if req.description is not None else policy.description
        policy.policies = req.policies if req.policies is not None else policy.policies

        policy.resource_status = ResourceStatusEnum.committed
        try:
            await self._engine.save(policy)
        except Exception as e:
            return None, e

        await self._notify_policy_reload()
        return policy, None

    async def delete(
            self,
            app,
            req: Union[PolicyDeleteRequest, Type[PolicyDeleteRequest]]
    ) -> Tuple[Optional[RBACPolicyModelV2], Optional[Exception]]:
        """
        Delete a Policy.
        """
        policy = await self._engine.find_one(RBACPolicyModelV2, RBACPolicyModelV2.subject_uuid == req.subject_uuid)
        if policy is None:
            return None, Exception(errors.policy_not_found)

        # default policy cannot be deleted
        if policy.name == RBAC_DEFAULT_POLICY_NAME:
            return None, Exception(errors.policy_cannot_be_deleted)

        try:
            await self._engine.delete(policy)
        except Exception as e:
            return None, e

        await self._notify_policy_reload()
        return policy, None

    async def _notify_policy_reload(self) -> bool:
        async with rbac_client.ApiClient(self._configuration) as api_client:
            _policy_instance = rbac_client.PolicyApi(api_client=api_client)
            try:
                response = await _policy_instance.postpolicy_policy_reload()
                if response.status == http.HTTPStatus.OK:
                    return True
                else:
                    return False
            except aiohttp.ClientError as e:
                logger.exception(e)
                return False

    async def _notify_policy_add(self, policy: RBACPolicyModelV2) -> bool:
        # TODO: currently not implemented because its less important, just reload the policy every time
        return await self._notify_policy_reload()

    async def enforce(self, app, subject: str, action: str, resource: str) -> bool:
        """
        Enforce a policy.
        """
        req = rbac_client.EnforceRequest1(subject=subject, action=action, object=resource)
        async with rbac_client.ApiClient(self._configuration) as api_client:
            _enforce_instance = rbac_client.EnforceApi(api_client=api_client)
            try:
                response = await _enforce_instance.postenforce_enforce_post(req)
                if response.status == http.HTTPStatus.OK:
                    return bool(response.result)
                else:
                    return False
            except aiohttp.ClientError as e:
                logger.exception(e)
                return False
