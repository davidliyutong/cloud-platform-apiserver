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
# Reasons we surface verbatim to the user; anything else is summarized generically.
_K8S_USER_VISIBLE_WAITING_REASONS = {
    "ImagePullBackOff",
    "ErrImagePull",
    "CrashLoopBackOff",
    "CreateContainerConfigError",
    "InvalidImageName",
    "RunContainerError",
}
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

    async def wait_pod(
            self,
            pod_id: str,
            target_status: PodStatusEnum,
            timeout_s: int = 120,
    ) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Wait for a pod (deployment) to reach the target status.

        Returns a (reason, error) tuple. On success both are None. On failure
        ``reason`` carries a short human-readable explanation suitable for
        surfacing to the end user (e.g. "FailedScheduling: 0/3 nodes available:
        3 Insufficient memory").

        ``error`` distinguishes the failure mode:

        - ``errors.k8s_pod_failed`` — the pod has hit a terminal problem
          (unschedulable, ImagePullBackOff, CrashLoopBackOff, …); detected
          early without waiting for the full timeout. ``reason`` is set.
        - ``errors.k8s_timeout`` — the deployment never reached
          ``target_status`` within ``timeout_s`` and no terminal reason was
          surfaced. ``reason`` may or may not be set.
        - ``errors.k8s_failed_to_update`` — the K8s API call itself errored.
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
                    return None, None

                # early detect un-recoverable problems (image pull, scheduling)
                # so we don't have to wait the full timeout.
                reason = await self.get_pod_failure_reason(pod_id)
                if reason is not None:
                    logger.warning(f"pod {pod_id} failed: {reason}")
                    return reason, errors.k8s_pod_failed

                if (time.time() - start_t) > timeout_s:
                    logger.warning(
                        f"pod {pod_id} status is {_current_status}, timeout"
                    )
                    return None, errors.k8s_timeout

                await asyncio.sleep(2)

            except ApiException as e:
                logger.exception(e)
                return None, errors.k8s_failed_to_update

    async def get_pod_failure_reason(self, pod_id: str) -> Optional[str]:
        """
        Inspect the underlying K8s Pods for this deployment and return a short
        explanation if one of them is unschedulable or otherwise stuck.

        Returns ``None`` when no actionable problem is visible (e.g. the pod is
        still starting normally).
        """
        try:
            pod_label = CONFIG_K8S_POD_LABEL_FMT.format(pod_id)
            ret = self.v1.list_namespaced_pod(
                self.namespace,
                label_selector=f"{CONFIG_K8S_POD_LABEL_KEY}={pod_label}",
            )
        except ApiException as e:
            logger.warning(f"failed to list pods for failure-reason lookup: {e}")
            return None
        except Exception as e:
            logger.warning(f"unexpected error listing pods for failure-reason lookup: {e}")
            return None

        for p in (ret.items or []):
            status = p.status
            if status is None:
                continue

            # PodScheduled=False is what surfaces "insufficient cpu/memory/gpu"
            # from kube-scheduler.
            for cond in (status.conditions or []):
                if cond.type == "PodScheduled" and cond.status == "False":
                    return self._format_reason(cond.reason, cond.message)

            # Container can't start (bad image, config error, crash loop, ...).
            for cs in (status.container_statuses or []):
                waiting = getattr(cs.state, "waiting", None) if cs.state else None
                if waiting and waiting.reason in _K8S_USER_VISIBLE_WAITING_REASONS:
                    return self._format_reason(waiting.reason, waiting.message)

        return None

    @staticmethod
    def _format_reason(reason: Optional[str], message: Optional[str]) -> str:
        reason = (reason or "").strip()
        message = (message or "").strip()
        if reason and message:
            return f"{reason}: {message}"
        return reason or message or "unknown scheduling failure"

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
