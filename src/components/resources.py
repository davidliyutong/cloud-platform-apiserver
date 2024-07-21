"""
This file contains K8S resources used to operate
# TODO: get rid of this
"""
import io
from typing import Dict, Any, Self, List

import yaml
from pydantic import BaseModel, model_validator

from src.components import config
from src.components.config import APIServerConfig
from src.components.datamodels.pod import PodModelV1
from src.components.utils import render_template_str


class K8SIngressResource(BaseModel):
    pod_values: Dict[Any, Any]
    auth_values: Dict[Any, Any]
    k8s_values: Dict[Any, Any]
    _K8S_INGRESS_TEMPLATE = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  labels:
    k8s-app: ${{ POD_LABEL }}
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "40960M"
    # nginx.ingress.kubernetes.io/auth-realm: Enter your credentials
    # nginx.ingress.kubernetes.io/auth-secret: ${{ POD_AUTH }}
    # nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-always-set-cookie: 'true'
    nginx.ingress.kubernetes.io/auth-cache-key: $cookie__${{ CONFIG_AUTH_COOKIES_NAME }}
    nginx.ingress.kubernetes.io/auth-url: ${{ CONFIG_AUTH_ENDPOINT }}/v1/auth/jwt/validate/${{ POD_USERNAME }}
  name: clpl-ingress-${{ POD_ID }}
spec:
  ingressClassName: ${{ CONFIG_NGINX_CLASS }} # CHANGE ME
  rules:
  - host: ${{ POD_ID }}.${{ CONFIG_CODER_HOSTNAME }} # CHANGE ME
    http:
      paths:
      - backend:
          service:
            name: clpl-svc-${{ POD_ID }}
            port:
              number: 3000
        path: /
        pathType: Prefix
  - host: ${{ POD_ID }}.${{ CONFIG_VNC_HOSTNAME }} # CHANGE ME
    http:
      paths:
      - backend:
          service:
            name: clpl-svc-${{ POD_ID }}
            port:
              number: 6080
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - ${{ POD_ID }}.${{ CONFIG_CODER_HOSTNAME }} # CHANGE ME hostname
    secretName: ${{ CONFIG_CODER_TLS_SECRET }} # CHANGE ME TLS Secret
  - hosts:
    - ${{ POD_ID }}.${{ CONFIG_VNC_HOSTNAME }} # CHANGE ME hostname
    secretName: ${{ CONFIG_VNC_TLS_SECRET }} # CHANGE ME TLS Secret
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  labels:
    k8s-app: ${{ POD_LABEL }}
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "40960M"
  name: clpl-ingress-${{ POD_ID }}-ssh
spec:
  ingressClassName: ${{ CONFIG_NGINX_CLASS }} # CHANGE ME
  rules:
  - host: ${{ POD_ID }}.${{ CONFIG_SSH_HOSTNAME }} # CHANGE ME
    http:
      paths:
      - backend:
          service:
            name: clpl-svc-${{ POD_ID }}
            port:
              number: 22
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - ${{ POD_ID }}.${{ CONFIG_SSH_HOSTNAME }} # CHANGE ME hostname
    secretName: ${{ CONFIG_SSH_TLS_SECRET }} # CHANGE ME TLS Secret
"""
# app.kubernetes.io/managed-by: CLPL

    @classmethod
    def new(cls, pod: PodModelV1, opt: APIServerConfig) -> Self:
        return cls(
            pod_values=pod.values,
            auth_values={
                "CONFIG_AUTH_COOKIES_NAME": config.CONFIG_AUTH_COOKIES_NAME,
                "CONFIG_AUTH_ENDPOINT": opt.site_config.auth_endpoint
            },
            k8s_values={
                "CONFIG_CODER_HOSTNAME": opt.site_config.coder_hostname,
                "CONFIG_CODER_TLS_SECRET": opt.site_config.coder_tls_secret,
                "CONFIG_VNC_HOSTNAME": opt.site_config.vnc_hostname,
                "CONFIG_VNC_TLS_SECRET": opt.site_config.vnc_tls_secret,
                "CONFIG_SSH_HOSTNAME": opt.site_config.ssh_hostname,
                "CONFIG_SSH_TLS_SECRET": opt.site_config.ssh_tls_secret,
                "CONFIG_NGINX_CLASS": opt.site_config.nginx_class,
            }
        )

    __EXAMPLE_VALUES__ = {
        "POD_LABEL": config.CONFIG_K8S_POD_LABEL_FMT.format("test_id"),
        "POD_ID": "test_id",
        "POD_AUTH": config.CONFIG_K8S_CREDENTIAL_FMT.format("username"),
        "POD_USERNAME": "username",
        "TEMPLATE_IMAGE_REF": "davidliyutong/code-server-speit:latest",
        "CONFIG_AUTH_COOKIES_NAME": "clpl_auth_token",
        "CONFIG_CODER_HOSTNAME": "code.example.org",
        "CONFIG_CODER_TLS_SECRET": "code-tls-secret",
        "CONFIG_VNC_HOSTNAME": "vnc.example.org",
        "CONFIG_VNC_TLS_SECRET": "vnc-tls-secret",
        "CONFIG_SSH_HOSTNAME": "ssh.example.org",
        "CONFIG_SSH_TLS_SECRET": "ssh-tls-secret",
        "CONFIG_NGINX_CLASS": "nginx",
    }

    @model_validator(mode="after")
    def validate_resource(self) -> bool:
        """
        This method validates resource to prevent illegal ingress resource
        """
        template_str, used_keys, _ = render_template_str(self._K8S_INGRESS_TEMPLATE, self.__EXAMPLE_VALUES__)
        return len(set(used_keys)) == len(self.__EXAMPLE_VALUES__)

    def render(self) -> List[Dict[Any, Any]]:
        """
        This method generate a dictionary that can be used to call k8s api
        """
        kv = self.pod_values | self.auth_values | self.k8s_values
        rendered_template_str, _, err = render_template_str(self._K8S_INGRESS_TEMPLATE, kv)
        return list(yaml.safe_load_all(io.StringIO(rendered_template_str)))
