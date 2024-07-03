from typing import Any

from pydantic import BaseModel

from src import CONFIG_PROJECT_NAME


class APIServerConfigMapping(BaseModel):
    name: str
    cli_name: str
    bind_env_name: str
    vyper_name: str
    type: type
    default: Any
    help: str


_api_config_mapping = {
    "debug": APIServerConfigMapping(
        name="debug",
        cli_name="debug",
        bind_env_name="debug",
        vyper_name="debug",
        type=bool,
        default=False,
        help="debug"
    ),
    "api_num_workers": APIServerConfigMapping(
        name="api_num_workers",
        cli_name="api.numWorkers",
        bind_env_name="api.numWorkers",
        vyper_name="api.numWorkers",
        type=int,
        default=4,
        help="api num workers"
    ),
    "api_host": APIServerConfigMapping(
        name="api_host",
        cli_name="api.host",
        bind_env_name="api.host",
        vyper_name="api.host",
        type=str,
        default="127.0.0.1",
        help="api host"
    ),
    "api_port": APIServerConfigMapping(
        name="api_port",
        cli_name="api.port",
        bind_env_name="api.port",
        vyper_name="api.port",
        type=int,
        default=8080,
        help="api port"
    ),
    "api_access_log": APIServerConfigMapping(
        name="api_access_log",
        cli_name="api.accessLog",
        bind_env_name="api.accessLog",
        vyper_name="api.accessLog",
        type=bool,
        default=False,
        help="api accessLog enable"
    ),
    "rbac_num_workers": APIServerConfigMapping(
        name="rbac_num_workers",
        cli_name="rbacserver.numWorkers",
        bind_env_name="rbacserver.numWorkers",
        vyper_name="rbacserver.numWorkers",
        type=int,
        default=4,
        help="rbacserver num workers"
    ),
    "rbac_port": APIServerConfigMapping(
        name="rbac_port",
        cli_name="rbacserver.port",
        bind_env_name="rbacserver.port",
        vyper_name="rbacserver.port",
        type=int,
        default=8081,
        help="rbacserver port"
    ),
    "rbac_access_log": APIServerConfigMapping(
        name="rbac_access_log",
        cli_name="rbacserver.accessLog",
        bind_env_name="rbacserver.accessLog",
        vyper_name="rbacserver.accessLog",
        type=bool,
        default=False,
        help="rbacserver accessLog enable"
    ),
    "db_host": APIServerConfigMapping(
        name="db_host",
        cli_name="db.host",
        bind_env_name="db.host",
        vyper_name="db.host",
        type=str,
        default="127.0.0.1",
        help="db host"
    ),
    "db_port": APIServerConfigMapping(
        name="db_port",
        cli_name="db.port",
        bind_env_name="db.port",
        vyper_name="db.port",
        type=int,
        default=27017,
        help="db port"
    ),
    "db_username": APIServerConfigMapping(
        name="db_username",
        cli_name="db.username",
        bind_env_name="db.username",
        vyper_name="db.username",
        type=str,
        default=CONFIG_PROJECT_NAME,
        help="db username"
    ),
    "db_password": APIServerConfigMapping(
        name="db_password",
        cli_name="db.password",
        bind_env_name="db.password",
        vyper_name="db.password",
        type=str,
        default=CONFIG_PROJECT_NAME,
        help="db password"
    ),
    "db_database": APIServerConfigMapping(
        name="db_database",
        cli_name="db.database",
        bind_env_name="db.database",
        vyper_name="db.database",
        type=str,
        default=CONFIG_PROJECT_NAME,
        help="db database"
    ),
    "k8s_host": APIServerConfigMapping(
        name="k8s_host",
        cli_name="k8s.host",
        bind_env_name="k8s.host",
        vyper_name="k8s.host",
        type=str,
        default="10.96.0.1",
        help="k8s host"
    ),
    "k8s_port": APIServerConfigMapping(
        name="k8s_port",
        cli_name="k8s.port",
        bind_env_name="k8s.port",
        vyper_name="k8s.port",
        type=int,
        default=6443,
        help="k8s port"
    ),
    "k8s_ca_cert": APIServerConfigMapping(
        name="k8s_ca_cert",
        cli_name="k8s.caCert",
        bind_env_name="k8s.caCert",
        vyper_name="k8s.caCert",
        type=str,
        default="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
        help="k8s certificate path"
    ),
    "k8s_token": APIServerConfigMapping(
        name="k8s_token",
        cli_name="k8s.token",
        bind_env_name="k8s.token",
        vyper_name="k8s.token",
        type=str,
        default="/var/run/secrets/kubernetes.io/serviceaccount/token",
        help="k8s token path"
    ),
    "k8s_verify_ssl": APIServerConfigMapping(
        name="k8s_verify_ssl",
        cli_name="k8s.verifySSL",
        bind_env_name="k8s.verifySSL",
        vyper_name="k8s.verifySSL",
        type=bool,
        default=False,
        help="k8s verifySSL option"
    ),
    "k8s_namespace": APIServerConfigMapping(
        name="k8s_namespace",
        cli_name="k8s.namespace",
        bind_env_name="k8s.namespace",
        vyper_name="k8s.namespace",
        type=str,
        default=CONFIG_PROJECT_NAME,
        help="k8s namespace"
    ),
    "oidc_config_name": APIServerConfigMapping(
        name="oidc_config_name",
        cli_name="oidc.configName",
        bind_env_name="oidc.configName",
        vyper_name="oidc.configName",
        type=str,
        default="",
        help="oidc config name in k8s cluster"
    ),
    "bootstrap_admin_username": APIServerConfigMapping(
        name="bootstrap_admin_username",
        cli_name="bootstrap.adminUsername",
        bind_env_name="bootstrap.adminUsername",
        vyper_name="bootstrap.adminUsername",
        type=str,
        default="admin",
        help="bootstrap admin username"
    ),
    "bootstrap_admin_password": APIServerConfigMapping(
        name="bootstrap_admin_password",
        cli_name="bootstrap.adminPassword",
        bind_env_name="bootstrap.adminPassword",
        vyper_name="bootstrap.adminPassword",
        type=str,
        default="admin",
        help="bootstrap admin password"
    ),
    "config_token_secret": APIServerConfigMapping(
        name="config_token_secret",
        cli_name="config.tokenSecret",
        bind_env_name="config.tokenSecret",
        vyper_name="config.tokenSecret",
        type=str,
        default=None,
        help="config tokenSecret"
    ),
    "config_token_expire_s": APIServerConfigMapping(
        name="config_token_expire_s",
        cli_name="config.tokenExpireS",
        bind_env_name="config.tokenExpireS",
        vyper_name="config.tokenExpireS",
        type=int,
        default=3600,
        help="config tokenExpireS"
    ),
    "config_use_oidc": APIServerConfigMapping(
        name="config_use_oidc",
        cli_name="config.useOIDC",
        bind_env_name="config.useOIDC",
        vyper_name="config.useOIDC",
        type=bool,
        default=False,
        help="config useOIDC"
    ),
    "site_config_name": APIServerConfigMapping(
        name="site_config_name",
        cli_name="site.configName",
        bind_env_name="site.configName",
        vyper_name="site.configName",
        type=str,
        default="",
        help="site config name in k8s cluster"
    ),
}
