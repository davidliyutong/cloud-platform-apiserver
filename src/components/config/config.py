"""
Configuration Component
"""

import argparse
import os
import os.path as osp
from typing import List, Tuple, Optional

import yaml
from loguru import logger
from pydantic import BaseModel, Field, model_validator
from vyper import Vyper

from src import CONFIG_PROJECT_NAME
from .params import _api_config_mapping

CONFIG_CONFIG_NAME = "apiserver"
CONFIG_HOME_PATH = os.path.expanduser('~')
CONFIG_DEFAULT_CONFIG_SEARCH_PATH = osp.join(CONFIG_HOME_PATH, ".config", CONFIG_PROJECT_NAME)
CONFIG_DEFAULT_CONFIG_PATH = osp.join(CONFIG_DEFAULT_CONFIG_SEARCH_PATH, f"{CONFIG_CONFIG_NAME}.yaml")


class OIDCConfig(BaseModel):
    name: str = Field(default=CONFIG_PROJECT_NAME)
    base_url: str = Field(alias="baseURL")
    authorization_url: str = Field(alias="authorizationURL", default="")
    token_url: str = Field(alias="tokenURL", default="")
    user_info_url: str = Field(alias="userInfoURL", default="")
    logout_url: str = Field(alias="logoutURL", default="")
    jwks_url: str = Field(alias="jwksURL", default="")
    frontend_login_url: str = Field(alias="frontendLoginURL")
    client_id: str = Field(alias="clientID")
    client_secret: str = Field(alias="clientSecret")
    redirect_url: str = Field(alias="redirectURL")
    scope: List[str] = Field(default=["openid"])
    scope_delimiter: str = Field(alias="scopeDelimiter", default="+")
    response_type: str = Field(alias="responseType", default="code")
    grant_type: str = Field(alias="grantType", default="authorization_code")
    user_filter: str = Field(alias="userFilter", default="{}")  # {"$and": [{"organize.id": "26000"}]}
    user_info_path: str = Field(alias="userInfoPath", default="$")  # entities[0]
    username_path: str = Field(alias="usernamePath", default="preferred_username")  # account
    email_path: str = Field(alias="emailPath", default="email")

    @staticmethod
    def alias_generator(name: str):
        return name.replace("_", "-")


class SiteConfig(BaseModel):
    auth_endpoint: str = Field(alias="authEndpoint")
    coder_hostname: str = Field(alias="coderHostname")
    coder_tls_secret: str = Field(alias="coderTLSSecret")
    vnc_hostname: str = Field(alias="vncHostname")
    vnc_tls_secret: str = Field(alias="vncTLSSecret")
    ssh_hostname: str = Field(alias="sshHostname")
    ssh_tls_secret: str = Field(alias="sshTLSSecret")
    nginx_class: str = Field(alias="nginxClass")

    @model_validator(mode="after")
    def check_fields(self):
        if any([
            self.auth_endpoint == "",
            self.coder_hostname == "",
            self.coder_tls_secret == "",
            self.vnc_hostname == "",
            self.vnc_tls_secret == "",
            self.ssh_hostname == "",
            self.ssh_tls_secret == "",
            self.nginx_class == "",
        ]):
            raise ValueError("site config fields must not be empty")


class APIServerConfig(BaseModel):
    debug: bool = _api_config_mapping["debug"].default

    api_num_workers: int = _api_config_mapping["api_num_workers"].default
    api_host: str = _api_config_mapping["api_host"].default
    api_port: int = _api_config_mapping["api_port"].default
    api_access_log: bool = _api_config_mapping["api_access_log"].default

    rbac_num_workers: int = _api_config_mapping["rbac_num_workers"].default
    rbac_port: int = _api_config_mapping["rbac_port"].default
    rbac_access_log: bool = _api_config_mapping["rbac_access_log"].default

    db_host: str = _api_config_mapping["db_host"].default
    db_port: int = _api_config_mapping["db_port"].default
    db_username: str = _api_config_mapping["db_username"].default
    db_password: str = _api_config_mapping["db_password"].default
    db_database: str = _api_config_mapping["db_database"].default

    k8s_host: str = _api_config_mapping["k8s_host"].default
    k8s_port: int = _api_config_mapping["k8s_port"].default
    k8s_ca_cert: str = _api_config_mapping["k8s_ca_cert"].default
    k8s_token: str = _api_config_mapping["k8s_token"].default
    k8s_verify_ssl: bool = _api_config_mapping["k8s_verify_ssl"].default
    k8s_namespace: str = _api_config_mapping["k8s_namespace"].default

    oidc_config_name: str = _api_config_mapping["oidc_config_name"].default
    oidc_config: Optional[OIDCConfig] = None

    bootstrap_admin_username: str = _api_config_mapping["bootstrap_admin_username"].default
    bootstrap_admin_password: str = _api_config_mapping["bootstrap_admin_password"].default

    config_token_secret: str = _api_config_mapping["config_token_secret"].default
    config_token_expire_s: int = _api_config_mapping["config_token_expire_s"].default
    config_use_oidc: bool = _api_config_mapping["config_use_oidc"].default

    site_config_name: str = _api_config_mapping["site_config_name"].default
    site_config: Optional[SiteConfig] = None

    @logger.catch
    def from_vyper(self, v: Vyper):
        # >>> Define Values >>>
        for name in _api_config_mapping.keys():
            if _api_config_mapping[name].type == bool:
                self.__setattr__(name, v.get_bool(_api_config_mapping[name].vyper_name))
            else:
                self.__setattr__(name, _api_config_mapping[name].type(v.get(_api_config_mapping[name].vyper_name)))
        # <<< Define Values <<<

        # override k8s_host and k8s_port if in k8s cluster
        if k8s_service_host := os.environ.get("KUBERNETES_SERVICE_HOST") is not None:
            self.k8s_host = k8s_service_host
        if k8s_service_port := os.environ.get("KUBERNETES_SERVICE_PORT") is not None:
            self.k8s_port = k8s_service_port

        return self

    @classmethod
    def get_default_config(cls) -> Vyper:
        v = Vyper()

        # >>> Set Default Values >>>
        for name in _api_config_mapping.keys():
            v.set_default(_api_config_mapping[name].vyper_name, _api_config_mapping[name].default)
        # <<< Set Default Values <<<

        return v

    @staticmethod
    def get_cli_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", type=str, help="config file path", default=None)

        # >>> Set Default Values >>>
        for name in _api_config_mapping.keys():
            parser.add_argument(f"--{_api_config_mapping[name].cli_name}", type=_api_config_mapping[name].type,
                                            help=_api_config_mapping[name].help)
        # <<< Set Default Values <<<

        return parser

    @classmethod
    def load_config(cls, argv: List[str]) -> Tuple[Vyper, Optional[Exception]]:
        parser = cls.get_cli_parser()
        args = parser.parse_args(argv)

        v = cls.get_default_config()
        v.set_config_name(CONFIG_CONFIG_NAME)
        v.set_config_type("yaml")
        v.add_config_path(f"/etc/{CONFIG_PROJECT_NAME}")
        v.add_config_path(CONFIG_DEFAULT_CONFIG_SEARCH_PATH)
        v.add_config_path(".")
        if args.config is not None:
            v.set_config_file(args.config)
        try:
            v.merge_in_config()
            logger.debug(f"load config form : {v._config_file}")
        except FileNotFoundError:
            v = cls.get_default_config()
            logger.warning(f"config file not found")

        v.set_env_prefix(CONFIG_PROJECT_NAME.upper())
        v.set_env_key_replacer(".", "_")

        v.bind_args(vars(args))

        # >>> Set Env Values >>>
        for name in _api_config_mapping.keys():
            v.bind_env(_api_config_mapping[name].bind_env_name)
        # <<< Set Env Values <<<

        return v, None

    @classmethod
    def save_config(cls, v: Vyper, path: str = None) -> Optional[Exception]:
        if path is None:
            path = CONFIG_DEFAULT_CONFIG_PATH

        _DIR = osp.dirname(path)
        if not osp.exists(_DIR):
            os.makedirs(_DIR, exist_ok=True)

        _VALUE = cls().from_vyper(v).model_dump()

        logger.debug(f"save path: {path}")
        logger.debug(f"save config: {_VALUE}")

        with open(path, "w") as f:
            yaml.dump(_VALUE, f, default_flow_style=False)

        return None

    def verify(self) -> Tuple[bool, Optional[Exception]]:
        msg = []
        if any([
            (self.config_use_oidc and self.oidc_config is None) and (msg.append("no oidc_config") == None),
            self.site_config is None and (msg.append("no site_config") == None),
        ]):
            return False, Exception("\n".join(msg))
        else:
            return True, None
