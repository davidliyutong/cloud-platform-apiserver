"""
K8SOperator service
"""
import asyncio
import base64
import io
import time
from typing import Optional, Tuple

import kubernetes
import yaml
from kubernetes import client
from kubernetes.client import ApiException
from loguru import logger

from src.components import errors
from src.components.config import (
    CONFIG_K8S_CREDENTIAL_FMT,
    CONFIG_K8S_POD_LABEL_FMT,
    CONFIG_K8S_POD_LABEL_KEY,
    CONFIG_K8S_NAMESPACE,
    CONFIG_K8S_SERVICE_FMT, CONFIG_K8S_DEPLOYMENT_FMT
)
from src.components.datamodels import PodStatusEnum
from src.components.resources import K8SIngressResource
from .common import ServiceInterface


class K8SOperatorService(ServiceInterface):

    def __init__(self, c: Optional[client], namespace: str = CONFIG_K8S_NAMESPACE):
        super().__init__()
        self.client = c
        self.namespace = namespace
        self.v1 = self.client.CoreV1Api()
        self.app_v1 = self.client.AppsV1Api()
        self.networking_v1 = self.client.NetworkingV1Api()

        # a dictionary that maps resource name to its corresponding function
        self._resource_function_map = {
            'Deployment': {
                'create': self.app_v1.create_namespaced_deployment,
                'update': self.app_v1.replace_namespaced_deployment,
                'get': self.app_v1.read_namespaced_deployment,
                'delete': self.app_v1.delete_namespaced_deployment,
                'list': self.app_v1.list_namespaced_deployment,
            },
            'Service': {
                'create': self.v1.create_namespaced_service,
                'update': self.v1.patch_namespaced_service,
                'get': self.v1.read_namespaced_service,
                'delete': self.v1.delete_namespaced_service,
                'list': self.v1.list_namespaced_service,
            },
            'Ingress': {
                'create': self.networking_v1.create_namespaced_ingress,
                'update': self.networking_v1.patch_namespaced_ingress,
                'get': self.networking_v1.read_namespaced_ingress,
                'delete': self.networking_v1.delete_namespaced_ingress,
                'list': self.networking_v1.list_namespaced_ingress,
            },
            'PersistentVolumeClaim': {
                'create': self.v1.create_namespaced_persistent_volume_claim,
                'update': self.v1.patch_namespaced_persistent_volume_claim,
                'get': self.v1.read_namespaced_persistent_volume_claim,
                'delete': self.v1.delete_namespaced_persistent_volume_claim,
                'list': self.v1.list_namespaced_persistent_volume_claim,
            },  # TODO: add more resources
        }

    async def is_secret_exists(self, secret_name: str) -> Tuple[Optional[bool], Optional[Exception]]:
        """
        Check if a secret exists in the cluster
        """
        try:
            ret = self.v1.read_namespaced_secret(
                secret_name,
                self.namespace
            )
            if ret is not None:
                return True, None
            else:
                return False, None
        except ApiException as e:
            if e.reason == 'Not Found':
                return False, None
            else:
                logger.exception(e)
                return False, e

    async def is_pod_exists(self, pod_id: str) -> Tuple[Optional[bool], Optional[Exception]]:
        """
        Check if a pod exists in the cluster
        """
        try:
            ret = self.v1.read_namespaced_service(
                CONFIG_K8S_SERVICE_FMT.format(pod_id),
                self.namespace
            )
            if ret is not None:
                return False, None
            else:
                return False, None
        except ApiException as e:
            if e.reason == 'Not Found':
                return False, None
            else:
                logger.exception(e)
                return False, e

    async def create_or_update_user_credentials(self, user_uuid: str, htpasswd: bytes) -> Optional[Exception]:
        """
        Create or update user credentials in the cluster. Similar to kubectl apply
        """

        # calculate the secret name
        secret_name = CONFIG_K8S_CREDENTIAL_FMT.format(user_uuid)

        # check if the secret exists
        secret_exists, err = await self.is_secret_exists(secret_name)
        if err is not None:
            return err

        if secret_exists:
            try:
                # update the secret
                ret = self.v1.patch_namespaced_secret(
                    secret_name,
                    self.namespace,
                    kubernetes.client.V1Secret(
                        api_version="v1",
                        kind="Secret",
                        data={
                            "auth": base64.b64encode(htpasswd).decode()
                        },
                        metadata=kubernetes.client.V1ObjectMeta(
                            name=CONFIG_K8S_CREDENTIAL_FMT.format(user_uuid),
                            namespace=self.namespace
                        )
                    )
                )
                if ret is None:
                    return errors.k8s_failed_to_update
            except ApiException as e:
                logger.exception(e)
                return errors.k8s_failed_to_update
        else:
            try:
                # create the secret
                ret = self.v1.create_namespaced_secret(
                    self.namespace,
                    kubernetes.client.V1Secret(
                        api_version="v1",
                        kind="Secret",
                        data={
                            "auth": base64.b64encode(htpasswd).decode()
                        },
                        metadata=kubernetes.client.V1ObjectMeta(
                            name=CONFIG_K8S_CREDENTIAL_FMT.format(user_uuid),
                            namespace=self.namespace
                        )
                    )
                )
                if ret is None:
                    return errors.k8s_failed_to_create
            except ApiException as e:
                logger.exception(e)
                return errors.k8s_failed_to_update

        return None

    async def delete_user_credential(self, user_uuid: str) -> Optional[Exception]:
        """
        Delete user credentials in the cluster
        """

        # calculate the secret name
        secret_name = CONFIG_K8S_CREDENTIAL_FMT.format(user_uuid)

        # check if the secret exists
        secret_exists, err = await self.is_secret_exists(secret_name)
        if err is not None:
            return err

        if secret_exists:
            try:
                # delete the secret
                ret = self.v1.delete_namespaced_secret(
                    secret_name,
                    self.namespace,
                )
                if ret is None:
                    logger.warning(f"failed to delete k8s secret {CONFIG_K8S_CREDENTIAL_FMT.format(user_uuid)}")
                    return errors.k8s_failed_to_delete
                else:
                    return None
            except ApiException as e:
                logger.exception(e)
                return errors.k8s_failed_to_update
        else:
            # secret does not exist
            return None

    async def create_or_update_pod(self, pod_id: str, template_str: str) -> Optional[Exception]:
        """
        Create or update a pod in the cluster. Similar to kubectl apply
        """
        try:
            # load multi documents yaml
            resources = yaml.safe_load_all(io.StringIO(template_str))
        except Exception as e:
            logger.exception(e)
            return e

        try:
            # apply each resource, except Ingress
            for resource in filter(lambda x: x['kind'] not in ['Ingress'], resources):
                err = await self._apply_k8s_resource(resource)
                if err is not None:
                    return err
        except Exception as e:
            logger.exception(e)
            return e

        logger.info(f"pod {pod_id} created or updated successfully")
        return None

    async def wait_pod(self, pod_id: str, target_status: PodStatusEnum, timeout_s: int = 120) -> Optional[Exception]:
        """
        This method wait for a pod(deployment) to update
        """
        start_t = time.time()
        while True:
            try:
                # check the status of deployment
                ret = self.app_v1.read_namespaced_deployment_status(
                    CONFIG_K8S_DEPLOYMENT_FMT.format(pod_id),
                    self.namespace
                )

                # check if the status is the target status
                _current_status = PodStatusEnum.from_k8s_status(ret.status)

                if _current_status == target_status:
                    logger.info(f"pod {pod_id} status is {target_status}")
                    return None
                elif (time.time() - start_t) > timeout_s:
                    logger.warning(f"pod {pod_id} status is {_current_status}, timeout")
                    return errors.k8s_timeout
                else:
                    await asyncio.sleep(2)

            except ApiException as e:
                logger.exception(e)
                return errors.k8s_failed_to_update

    async def delete_pod(self, pod_id: str) -> Optional[Exception]:
        """
        Delete a pod in the cluster
        """

        # calculate the pod label
        pod_label = CONFIG_K8S_POD_LABEL_FMT.format(pod_id)

        try:
            # for all types of related resources, including Ingress
            for _, col in self._resource_function_map.items():
                # get all resources with the pod label of this kind
                resources = col['list'](
                    self.namespace,
                    label_selector=f"{CONFIG_K8S_POD_LABEL_KEY}={pod_label}"
                )
                # delete each resource
                for resource in resources.items:
                    col['delete'](resource.metadata.name, self.namespace)

        except ApiException as e:
            logger.exception(e)
            return e

        except Exception as e:
            logger.exception(e)
            return e

        logger.info(f"pod {pod_id} deleted successfully")
        return None

    async def _apply_k8s_resource(self, resource: dict) -> Optional[Exception]:
        """
        Apply k8s resource, similar to kubectl apply
        """

        kind = resource['kind']
        try:
            # dynamically call the corresponding function and find if the resource exists
            self._resource_function_map[kind]['get'](resource['metadata']['name'], self.namespace)
            exists = True
        except ApiException as e:
            if e.reason == 'Not Found':
                exists = False
            else:
                logger.exception(e)
                return e

        if exists:
            try:
                # update the resource
                self._resource_function_map[kind]['update'](
                    resource['metadata']['name'],
                    self.namespace,
                    resource
                )
            except ApiException as e:
                logger.exception(e)
                return e
        else:
            try:
                # create the resource
                self._resource_function_map[kind]['create'](self.namespace, resource)
            except ApiException as e:
                logger.exception(e)
                return e

    async def create_apply_ingress(self, ingress_resource: K8SIngressResource) -> Optional[Exception]:
        tasks = [self._apply_k8s_resource(obj) for obj in ingress_resource.render()]
        res = await asyncio.gather(*tasks)
        if any(map(lambda x: x is not None, res)):
            logger.debug(res)
            return errors.k8s_failed_to_update
        else:
            return None
