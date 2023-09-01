"""
Configuration Component
"""

import argparse
import os
import os.path as osp
from typing import List, Any, Tuple, Optional, Dict

import yaml
from loguru import logger
from pydantic import BaseModel
from vyper import Vyper

CONFIG_BUILD_VERSION = "v0.0.5"
CONFIG_HOME_PATH = os.path.expanduser('~')
CONFIG_CONFIG_NAME = "apiserver"
CONFIG_PROJECT_NAME = "clpl"
CONFIG_AUTH_COOKIES_NAME = "clpl_auth_token"
CONFIG_PROXY_ORIGIN_URL_HEADER = "x-original-url"
CONFIG_LOG_PATH_KEY = CONFIG_PROJECT_NAME.upper() + "_LOG_PATH"
CONFIG_LOG_PATH_DEFAULT = "./logs/apiserver"
CONFIG_DEFAULT_CONFIG_SEARCH_PATH = osp.join(CONFIG_HOME_PATH, ".config", CONFIG_PROJECT_NAME)
CONFIG_DEFAULT_CONFIG_PATH = osp.join(CONFIG_DEFAULT_CONFIG_SEARCH_PATH, f"{CONFIG_CONFIG_NAME}.yaml")
CONFIG_EVENT_QUEUE_NAME = "clpl_event_queue"
CONFIG_GLOBAL_COLLECTION_NAME = "clpl_global"
CONFIG_USER_COLLECTION_NAME = "clpl_users"
CONFIG_POD_COLLECTION_NAME = "clpl_pods"
CONFIG_TEMPLATE_COLLECTION_NAME = "clpl_templates"
CONFIG_K8S_CREDENTIAL_FMT = "{}-basic-auth"
CONFIG_K8S_DEPLOYMENT_FMT = "clpl-{}"
CONFIG_K8S_POD_LABEL_FMT = "apps.clpl-{}"
CONFIG_K8S_POD_LABEL_KEY = "k8s-app"
CONFIG_K8S_SERVICE_FMT = "clpl-svc-{}"
CONFIG_K8S_NAMESPACE = "clpl"
CONFIG_SCAN_POD_INTERVAL_S = 120
CONFIG_HEARTBEAT_INTERVAL_S = 120
CONFIG_SHUTDOWN_GRACE_PERIOD_S = 60

CONFIG_DEVICE_TOKEN_EXPIRE_S = 7 * 24 * 60 * 60
CONFIG_DEVICE_TOKEN_RENEW_THRESHOLD_S = 6 * 24 * 60 * 60


class APIServerConfig(BaseModel):
    debug: bool = False

    api_num_workers: int = 4
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_access_log: bool = False

    mq_host: str = "127.0.0.1"
    mq_port: int = 5672
    mq_username: str = CONFIG_PROJECT_NAME
    mq_password: str = CONFIG_PROJECT_NAME
    mq_exchange: str = ""

    db_host: str = "127.0.0.1"
    db_port: int = 27017
    db_username: str = CONFIG_PROJECT_NAME
    db_password: str = CONFIG_PROJECT_NAME
    db_database: str = CONFIG_PROJECT_NAME

    k8s_host: str = "10.96.0.1"
    k8s_port: int = 6443
    k8s_ca_cert: str = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    k8s_token: str = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    k8s_verify_ssl: bool = False
    k8s_namespace: str = CONFIG_K8S_NAMESPACE

    oidc_name: str = "clpl"
    oidc_base_url: str = "https://authentik.example.com"
    oidc_authorization_url: str = ""
    oidc_token_url: str = ""
    oidc_user_info_url: str = ""
    oidc_logout_url: str = ""
    oidc_jwks_url: str = ""
    oidc_frontend_login_url: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_redirect_url: str = ""
    oidc_scope: List[str] = ["openid"]
    oidc_scope_delimiter: str = "+"
    oidc_response_type: str = "code"
    oidc_grant_type: str = "authorization_code"
    oidc_user_filter: str = "{}"  # {"$and": [{"organize.id": "26000"}]}
    oidc_user_info_path: str = "$"  # entities[0]
    oidc_username_path: str = "preferred_username"  # account
    oidc_email_path: str = "email"

    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "admin"

    config_token_secret: str = None
    config_token_expire_s: int = 3600
    config_auth_endpoint: str = ""
    config_coder_hostname: str = ""
    config_coder_tls_secret: str = ""
    config_vnc_hostname: str = ""
    config_vnc_tls_secret: str = ""
    config_use_oidc: bool = False

    @logger.catch
    def from_dict(self, d: Dict[str, Any]):
        # >>> Define Values >>>
        self.debug = bool(d["debug"])

        self.api_num_workers = int(d["api"]["numWorkers"])
        self.api_host = str(d["api"]["host"])
        self.api_port = int(d["api"]["port"])
        self.api_access_log = bool(d["api"]["accessLog"])

        self.db_host = str(d["db"]["host"])
        self.db_port = int(d["db"]["port"])
        self.db_username = str(d["db"]["username"])
        self.db_password = str(d["db"]["password"])
        self.db_database = str(d["db"]["database"])

        self.mq_host = str(d["mq"]["host"])
        self.mq_port = int(d["mq"]["port"])
        self.mq_username = str(d["mq"]["username"])
        self.mq_password = str(d["mq"]["password"])
        self.mq_exchange = str(d["mq"]["exchange"])

        self.k8s_host = str(d["k8s"]["host"])
        self.k8s_port = int(d["k8s"]["port"])
        self.k8s_ca_cert = str(d["k8s"]["caCert"])
        self.k8s_token = str(d["k8s"]["token"])
        self.k8s_verify_ssl = bool(d["k8s"]["verifySSL"])
        self.k8s_namespace = str(d["k8s"]["namespace"])

        self.oidc_name = str(d["oidc"]["name"])
        self.oidc_base_url = str(d["oidc"]["baseURL"])
        self.oidc_authorization_url = str(d["oidc"]["authorizationURL"])
        self.oidc_token_url = str(d["oidc"]["tokenURL"])
        self.oidc_user_info_url = str(d["oidc"]["userInfoURL"])
        self.oidc_logout_url = str(d["oidc"]["logoutURL"])
        self.oidc_jwks_url = str(d["oidc"]["jwksURL"])
        self.oidc_frontend_login_url = str(d["oidc"]["frontendLoginURL"])
        self.oidc_client_id = str(d["oidc"]["clientID"])
        self.oidc_client_secret = str(d["oidc"]["clientSecret"])
        self.oidc_redirect_url = str(d["oidc"]["redirectURL"])
        self.oidc_scope = list(d["oidc"]["scope"])
        self.oidc_scope_delimiter = str(d["oidc"]["scopeDelimiter"])
        self.oidc_response_type = str(d["oidc"]["responseType"])
        self.oidc_grant_type = str(d["oidc"]["grantType"])
        self.oidc_user_filter = str(d["oidc"]["userFilter"])
        self.oidc_user_info_path = str(d["oidc"]["userInfoPath"])
        self.oidc_username_path = str(d["oidc"]["usernamePath"])
        self.oidc_email_path = str(d["oidc"]["emailPath"])

        self.bootstrap_admin_password = str(d["bootstrap"]["adminPassword"])
        self.bootstrap_admin_username = str(d["bootstrap"]["adminUsername"])

        self.config_token_secret = str(d["config"]["tokenSecret"])
        self.config_token_expire_s = int(d["config"]["tokenExpireS"])
        self.config_auth_endpoint = str(d["config"]["authEndpoint"])
        self.config_coder_hostname = str(d["config"]["coderHostname"])
        self.config_coder_tls_secret = str(d["config"]["coderTLSSecret"])
        self.config_vnc_hostname = str(d["config"]["vncHostname"])
        self.config_vnc_tls_secret = str(d["config"]["vncTLSSecret"])
        self.config_use_oidc = bool(d["config"]["useOIDC"])
        # <<< Define Values <<<
        return self

    @logger.catch
    def from_vyper(self, v: Vyper):
        # >>> Define Values >>>
        self.debug = v.get_bool("debug")

        self.api_num_workers = v.get_int("api.numWorkers")
        self.api_host = v.get_string("api.host")
        self.api_port = v.get_int("api.port")
        self.api_access_log = v.get_bool("api.accessLog")

        self.db_host = v.get_string("db.host")
        self.db_port = v.get_int("db.port")
        self.db_username = v.get_string("db.username")
        self.db_password = v.get_string("db.password")
        self.db_database = v.get_string("db.database")

        self.mq_host = v.get_string("mq.host")
        self.mq_port = v.get_int("mq.port")
        self.mq_username = v.get_string("mq.username")
        self.mq_password = v.get_string("mq.password")
        self.mq_exchange = v.get_string("mq.exchange")

        self.k8s_host = v.get_string("k8s.host")
        self.k8s_port = v.get_int("k8s.port")
        self.k8s_ca_cert = v.get_string("k8s.caCert")
        self.k8s_token = v.get_string("k8s.token")
        self.k8s_verify_ssl = v.get_bool("k8s.verifySSL")
        self.k8s_namespace = v.get_string("k8s.namespace")

        self.oidc_name = v.get_string("oidc.name")
        self.oidc_base_url = v.get_string("oidc.baseURL")
        self.oidc_authorization_url = v.get_string("oidc.authorizationURL")
        self.oidc_token_url = v.get_string("oidc.tokenURL")
        self.oidc_user_info_url = v.get_string("oidc.userInfoURL")
        self.oidc_logout_url = v.get_string("oidc.logoutURL")
        self.oidc_jwks_url = v.get_string("oidc.jwksURL")
        self.oidc_frontend_login_url = v.get_string("oidc.frontendLoginURL")
        self.oidc_client_id = v.get_string("oidc.clientID")
        self.oidc_client_secret = v.get_string("oidc.clientSecret")
        self.oidc_redirect_url = v.get_string("oidc.redirectURL")
        self.oidc_scope = v.get_string("oidc.scope").split(v.get_string("oidc.scopeDelimiter"))
        self.oidc_scope_delimiter = v.get_string("oidc.scopeDelimiter")
        self.oidc_response_type = v.get_string("oidc.responseType")
        self.oidc_grant_type = v.get_string("oidc.grantType")
        self.oidc_user_filter = v.get_string("oidc.userFilter")
        self.oidc_user_info_path = v.get_string("oidc.userInfoPath")
        self.oidc_username_path = v.get_string("oidc.usernamePath")
        self.oidc_email_path = v.get_string("oidc.emailPath")

        self.bootstrap_admin_password = v.get_string("bootstrap.adminPassword")
        self.bootstrap_admin_username = v.get_string("bootstrap.adminUsername")

        self.config_token_secret = v.get_string("config.tokenSecret")
        self.config_token_expire_s = v.get_int("config.tokenExpireS")
        self.config_auth_endpoint = v.get_string("config.authEndpoint")
        self.config_coder_hostname = v.get_string("config.coderHostname")
        self.config_coder_tls_secret = v.get_string("config.coderTLSSecret")
        self.config_vnc_hostname = v.get_string("config.vncHostname")
        self.config_vnc_tls_secret = v.get_string("config.vncTLSSecret")
        self.config_use_oidc = v.get_bool("config.useOIDC")
        # <<< Define Values <<<

        return self

    def to_dict(self):
        # >>> Define Values >>>
        return {
            "debug": self.debug,
            "api": {
                "numWorkers": self.api_num_workers,
                "host": self.api_host,
                "port": self.api_port,
                "accessLog": self.api_access_log
            },
            "db": {
                "host": self.db_host,
                "port": self.db_port,
                "username": self.db_username,
                "password": self.db_password,
                "database": self.db_database,
            },
            "mq": {
                "host": self.mq_host,
                "port": self.mq_port,
                "username": self.mq_username,
                "password": self.mq_password,
                "exchange": self.mq_exchange,
            },
            "k8s": {
                "host": self.k8s_host,
                "port": self.k8s_port,
                "caCert": self.k8s_ca_cert,
                "token": self.k8s_token,
                "verifySSL": self.k8s_verify_ssl,
                "namespace": self.k8s_namespace,
            },
            "oidc": {
                "name": self.oidc_name,
                "baseURL": self.oidc_base_url,
                "authorizationURL": self.oidc_authorization_url,
                "tokenURL": self.oidc_token_url,
                "userInfoURL": self.oidc_user_info_url,
                "logoutURL": self.oidc_logout_url,
                "jwksURL": self.oidc_jwks_url,
                "frontendLoginURL": self.oidc_frontend_login_url,
                "clientID": self.oidc_client_id,
                "clientSecret": self.oidc_client_secret,
                "redirectURL": self.oidc_redirect_url,
                "scope": self.oidc_scope,
                "scopeDelimiter": self.oidc_scope_delimiter,
                "responseType": self.oidc_response_type,
                "grantType": self.oidc_grant_type,
                "userFilter": self.oidc_user_filter,
                "userInfoPath": self.oidc_user_info_path,
                "usernamePath": self.oidc_username_path,
                "emailPath": self.oidc_email_path,
            },
            "bootstrap": {
                "adminUsername": self.bootstrap_admin_username,
                "adminPassword": self.bootstrap_admin_password,
            },
            "config": {
                "tokenSecret": self.config_token_secret,
                "tokenExpireS": self.config_token_expire_s,
                "authEndpoint": self.config_auth_endpoint,
                "coderHostname": self.config_coder_hostname,
                "coderTLSSecret": self.config_coder_tls_secret,
                "vncHostname": self.config_vnc_hostname,
                "vncTLSSecret": self.config_vnc_tls_secret,
                "useOIDC": self.config_use_oidc,
            }
        }
        # <<< Define Values <<<

    def to_sanic_config(self):
        # >>> Define Values >>>
        return {
            "DEBUG": self.debug,
            "API_NUMWORKERS": self.api_num_workers,
            "API_HOST": self.api_host,
            "API_PORT": self.api_port,
            "API_ACCESS_LOG": self.api_access_log,
            "DB_HOST": self.db_host,
            "DB_PORT": self.db_port,
            "DB_USERNAME": self.db_username,
            "DB_PASSWORD": self.db_password,
            "DB_DATABASE": self.db_database,
            "MQ_HOST": self.mq_host,
            "MQ_PORT": self.mq_port,
            "MQ_USERNAME": self.mq_username,
            "MQ_PASSWORD": self.mq_password,
            "MQ_EXCHANGE": self.mq_exchange,
            "K8S_HOST": self.k8s_host,
            "K8S_PORT": self.k8s_port,
            "K8S_CACERT": self.k8s_ca_cert,
            "K8S_TOKEN": self.k8s_token,
            "K8S_VERIFY_SSL": self.k8s_verify_ssl,
            "K8S_NAMESPACE": self.k8s_namespace,
            "OIDC_NAME": self.oidc_name,
            "OIDC_BASE_URL": self.oidc_base_url,
            "OIDC_AUTHORIZATION_URL": self.oidc_authorization_url,
            "OIDC_TOKEN_URL": self.oidc_token_url,
            "OIDC_USER_INFO_URL": self.oidc_user_info_url,
            "OIDC_LOGOUT_URL": self.oidc_logout_url,
            "OIDC_JWKS_URL": self.oidc_jwks_url,
            "OIDC_FRONTEND_LOGIN_URL": self.oidc_frontend_login_url,
            "OIDC_CLIENT_ID": self.oidc_client_id,
            "OIDC_CLIENT_SECRET": self.oidc_client_secret,
            "OIDC_REDIRECT_URL": self.oidc_redirect_url,
            "OIDC_SCOPE": self.oidc_scope,
            "OIDC_SCOPE_DELIMITER": self.oidc_scope_delimiter,
            "OIDC_RESPONSE_TYPE": self.oidc_response_type,
            "OIDC_GRANT_TYPE": self.oidc_grant_type,
            "OIDC_USER_FILTER": self.oidc_user_filter,
            "OIDC_USER_INFO_PATH": self.oidc_user_info_path,
            "OIDC_USERNAME_PATH": self.oidc_username_path,
            "OIDC_EMAIL_PATH": self.oidc_email_path,
            "BOOTSTRAP_ADMIN_USERNAME": self.bootstrap_admin_username,
            "BOOTSTRAP_ADMIN_PASSWORD": self.bootstrap_admin_password,
            "CONFIG_TOKEN_SECRET": self.config_token_secret,
            "CONFIG_TOKEN_EXPIRE_S": self.config_token_expire_s,
            "CONFIG_AUTH_ENDPOINT": self.config_auth_endpoint,
            "CONFIG_CODER_HOSTNAME": self.config_coder_hostname,
            "CONFIG_CODER_TLS_SECRET": self.config_coder_tls_secret,
            "CONFIG_VNC_HOSTNAME": self.config_vnc_hostname,
            "CONFIG_VNC_TLS_SECRET": self.config_vnc_tls_secret,
            "CONFIG_USE_OIDC": self.config_use_oidc,
        }
        # <<< Define Values <<<

    @classmethod
    def get_default_config(cls) -> Vyper:
        v = Vyper()
        _DEFAULT: cls = cls()

        # >>> Set Default Values >>>
        v.set_default("debug", _DEFAULT.debug)

        v.set_default("api.numWorkers", _DEFAULT.api_num_workers)
        v.set_default("api.host", _DEFAULT.api_host)
        v.set_default("api.port", _DEFAULT.api_port)
        v.set_default("api.accessLog", _DEFAULT.api_access_log)

        v.set_default("db.host", _DEFAULT.db_host)
        v.set_default("db.port", _DEFAULT.db_port)
        v.set_default("db.username", _DEFAULT.db_username)
        v.set_default("db.password", _DEFAULT.db_password)
        v.set_default("db.database", _DEFAULT.db_database)

        v.set_default("mq.host", _DEFAULT.mq_host)
        v.set_default("mq.port", _DEFAULT.mq_port)
        v.set_default("mq.username", _DEFAULT.mq_username)
        v.set_default("mq.password", _DEFAULT.mq_password)
        v.set_default("mq.exchange", _DEFAULT.mq_exchange)

        v.set_default("k8s.host", _DEFAULT.k8s_host)
        v.set_default("k8s.port", _DEFAULT.k8s_port)
        v.set_default("k8s.caCert", _DEFAULT.k8s_ca_cert)
        v.set_default("k8s.token", _DEFAULT.k8s_token)
        v.set_default("k8s.verifySSL", _DEFAULT.k8s_verify_ssl)
        v.set_default("k8s.namespace", _DEFAULT.k8s_namespace)

        v.set_default("oidc.name", _DEFAULT.oidc_name)
        v.set_default("oidc.baseURL", _DEFAULT.oidc_base_url)
        v.set_default("oidc.authorizationURL", _DEFAULT.oidc_authorization_url)
        v.set_default("oidc.tokenURL", _DEFAULT.oidc_token_url)
        v.set_default("oidc.userInfoURL", _DEFAULT.oidc_user_info_url)
        v.set_default("oidc.logoutURL", _DEFAULT.oidc_logout_url)
        v.set_default("oidc.jwksURL", _DEFAULT.oidc_jwks_url)
        v.set_default("oidc.frontendLoginURL", _DEFAULT.oidc_frontend_login_url)
        v.set_default("oidc.clientID", _DEFAULT.oidc_client_id)
        v.set_default("oidc.clientSecret", _DEFAULT.oidc_client_secret)
        v.set_default("oidc.redirectURL", _DEFAULT.oidc_redirect_url)
        v.set_default("oidc.scope", _DEFAULT.oidc_scope_delimiter.join(_DEFAULT.oidc_scope))
        v.set_default("oidc.scopeDelimiter", _DEFAULT.oidc_scope_delimiter)
        v.set_default("oidc.responseType", _DEFAULT.oidc_response_type)
        v.set_default("oidc.grantType", _DEFAULT.oidc_grant_type)
        v.set_default("oidc.userFilter", _DEFAULT.oidc_user_filter)
        v.set_default("oidc.userInfoPath", _DEFAULT.oidc_user_info_path)
        v.set_default("oidc.usernamePath", _DEFAULT.oidc_username_path)
        v.set_default("oidc.emailPath", _DEFAULT.oidc_email_path)

        v.set_default("bootstrap.adminUsername", _DEFAULT.bootstrap_admin_username)
        v.set_default("bootstrap.adminPassword", _DEFAULT.bootstrap_admin_password)

        v.set_default("config.tokenSecret", _DEFAULT.config_token_secret)
        v.set_default("config.tokenExpireS", _DEFAULT.config_token_expire_s)
        v.set_default("config.authEndpoint", _DEFAULT.config_auth_endpoint)
        v.set_default("config.coderHostname", _DEFAULT.config_coder_hostname)
        v.set_default("config.coderTLSSecret", _DEFAULT.config_coder_tls_secret)
        v.set_default("config.vncHostname", _DEFAULT.config_vnc_hostname)
        v.set_default("config.vncTLSSecret", _DEFAULT.config_vnc_tls_secret)
        v.set_default("config.useOIDC", _DEFAULT.config_use_oidc)
        # <<< Set Default Values <<<

        return v

    @staticmethod
    def get_cli_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", type=str, help="config file path", default=None)

        # >>> Set Default Values >>>
        parser.add_argument("--debug", type=bool, help="debug")

        parser.add_argument("--api.numWorkers", type=int, help="api num workers")
        parser.add_argument("--api.host", type=str, help="api host")
        parser.add_argument("--api.port", type=int, help="api port")
        parser.add_argument("--api.accessLog", type=bool, help="api accessLog enable")

        parser.add_argument("--db.host", type=str, help="db host")
        parser.add_argument("--db.port", type=int, help="db port")
        parser.add_argument("--db.username", type=str, help="db username")
        parser.add_argument("--db.password", type=str, help="db password")
        parser.add_argument("--db.database", type=str, help="db database")

        parser.add_argument("--mq.host", type=str, help="mq host")
        parser.add_argument("--mq.port", type=int, help="mq port")
        parser.add_argument("--mq.username", type=str, help="mq username")
        parser.add_argument("--mq.password", type=str, help="mq password")
        parser.add_argument("--mq.exchange", type=str, help="mq exchange")

        parser.add_argument("--k8s.host", type=str, help="k8s host")
        parser.add_argument("--k8s.port", type=int, help="k8s port")
        parser.add_argument("--k8s.caCert", type=str, help="k8s caCert")
        parser.add_argument("--k8s.token", type=str, help="k8s token")
        parser.add_argument("--k8s.verifySSL", type=bool, help="k8s verifySSL")
        parser.add_argument("--k8s.namespace", type=str, help="k8s namespace")

        parser.add_argument("--oidc.name", type=str, help="oidc name")
        parser.add_argument("--oidc.baseURL", type=str, help="oidc baseURL")
        parser.add_argument("--oidc.authorizationURL", type=str, help="oidc authorizationURL")
        parser.add_argument("--oidc.tokenURL", type=str, help="oidc tokenURL")
        parser.add_argument("--oidc.userInfoURL", type=str, help="oidc userInfoURL")
        parser.add_argument("--oidc.logoutURL", type=str, help="oidc logoutURL")
        parser.add_argument("--oidc.jwksURL", type=str, help="oidc jwksURL")
        parser.add_argument("--oidc.frontendLoginURL", type=str, help="oidc frontendLoginURL")
        parser.add_argument("--oidc.clientID", type=str, help="oidc clientID")
        parser.add_argument("--oidc.clientSecret", type=str, help="oidc clientSecret")
        parser.add_argument("--oidc.redirectURL", type=str, help="oidc redirectURL")
        parser.add_argument("--oidc.scope", type=str, help="oidc scope")
        parser.add_argument("--oidc.scopeDelimiter", type=str, help="oidc scopeDelimiter")
        parser.add_argument("--oidc.responseType", type=str, help="oidc responseType")
        parser.add_argument("--oidc.grantType", type=str, help="oidc grantType")
        parser.add_argument("--oidc.userFilter", type=str, help="oidc userFilter")
        parser.add_argument("--oidc.userInfoPath", type=str, help="oidc userInfoPath")
        parser.add_argument("--oidc.usernamePath", type=str, help="oidc usernamePath")
        parser.add_argument("--oidc.emailPath", type=str, help="oidc emailPath")

        parser.add_argument("--bootstrap.adminUsername", type=str, help="bootstrap admin username")
        parser.add_argument("--bootstrap.adminPassword", type=str, help="bootstrap admin password")

        parser.add_argument("--config.tokenSecret", type=str, help="config tokenSecret")
        parser.add_argument("--config.tokenExpireS", type=int, help="config tokenExpireS")
        parser.add_argument("--config.authEndpoint", type=str, help="config authEndpoint")
        parser.add_argument("--config.coderHostname", type=str, help="config code hostname")
        parser.add_argument("--config.coderTLSSecret", type=str, help="config code tlsSecret")
        parser.add_argument("--config.vncHostname", type=str, help="config vnc hostname")
        parser.add_argument("--config.vncTLSSecret", type=str, help="config vnc tlsSecret")
        parser.add_argument("--config.useOIDC", type=bool, help="config useOIDC")
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
        v.bind_env("debug")

        v.bind_env("api.numWorkers")
        v.bind_env("api.host")
        v.bind_env("api.port")
        v.bind_env("api.accessLog")

        v.bind_env("db.host")
        v.bind_env("db.port")
        v.bind_env("db.username")
        v.bind_env("db.password")
        v.bind_env("db.database")

        v.bind_env("mq.host")
        v.bind_env("mq.port")
        v.bind_env("mq.username")
        v.bind_env("mq.password")
        v.bind_env("mq.exchange")

        v.bind_env("k8s.host")
        v.bind_env("k8s.port")
        v.bind_env("k8s.caCert")
        v.bind_env("k8s.token")
        v.bind_env("k8s.verifySSL")
        v.bind_env("k8s.namespace")

        v.bind_env("oidc.name")
        v.bind_env("oidc.baseURL")
        v.bind_env("oidc.authorizationURL")
        v.bind_env("oidc.tokenURL")
        v.bind_env("oidc.userInfoURL")
        v.bind_env("oidc.logoutURL")
        v.bind_env("oidc.jwksURL")
        v.bind_env("oidc.frontendLoginURL")
        v.bind_env("oidc.clientID")
        v.bind_env("oidc.clientSecret")
        v.bind_env("oidc.redirectURL")
        v.bind_env("oidc.scope")
        v.bind_env("oidc.scopeDelimiter")
        v.bind_env("oidc.responseType")
        v.bind_env("oidc.grantType")
        v.bind_env("oidc.userFilter")
        v.bind_env("oidc.userInfoPath")
        v.bind_env("oidc.usernamePath")
        v.bind_env("oidc.emailPath")

        v.bind_env("bootstrap.adminUsername")
        v.bind_env("bootstrap.adminPassword")

        v.bind_env("config.tokenSecret")
        v.bind_env("config.tokenExpireS")
        v.bind_env("config.authEndpoint")
        v.bind_env("config.coderHostname")
        v.bind_env("config.coderTLSSecret")
        v.bind_env("config.vncHostname")
        v.bind_env("config.vncTLSSecret")
        v.bind_env("config.useOIDC")
        # <<< Set Env Values <<<

        x = cls()
        x.from_vyper(v)
        logger.debug(f"watcher config: {cls().from_vyper(v).to_dict()}")

        return v, None

    @classmethod
    def save_config(cls, v: Vyper, path: str = None) -> Optional[Exception]:
        if path is None:
            path = CONFIG_DEFAULT_CONFIG_PATH

        _DIR = osp.dirname(path)
        if not osp.exists(_DIR):
            os.makedirs(_DIR, exist_ok=True)

        _VALUE = cls().from_vyper(v).to_dict()

        logger.debug(f"save path: {path}")
        logger.debug(f"save config: {_VALUE}")

        with open(path, "w") as f:
            yaml.dump(_VALUE, f, default_flow_style=False)

        return None

    @property
    def k8s_config_values(self):
        return {
            "CONFIG_CODER_HOSTNAME": self.config_coder_hostname,
            "CONFIG_CODER_TLS_SECRET": self.config_coder_tls_secret,
            "CONFIG_VNC_HOSTNAME": self.config_vnc_hostname,
            "CONFIG_VNC_TLS_SECRET": self.config_vnc_tls_secret,
        }

    @property
    def auth_config_values(self):
        return {
            "CONFIG_AUTH_COOKIES_NAME": CONFIG_AUTH_COOKIES_NAME,
            "CONFIG_AUTH_ENDPOINT": self.config_auth_endpoint
        }

    def verify(self) -> Tuple[bool, Optional[Exception]]:
        msg = []
        if any([
            self.config_auth_endpoint == "" and msg.append("no config_auth_endpoint"),
            self.config_use_oidc and any([
                self.oidc_frontend_login_url == "" and msg.append("no oidc_frontend_login_url"),
                self.oidc_client_id == "" and msg.append("no oidc_client_id"),
                self.oidc_client_secret == "" and msg.append("no oidc_client_secret"),
                self.oidc_redirect_url == "" and msg.append("no oidc_redirect_url"),
            ]),
            self.config_coder_hostname == "" and msg.append("no config_coder_hostname"),
            self.config_coder_tls_secret == "" and msg.append("no config_coder_tls_secret"),
            self.config_vnc_hostname == "" and msg.append("no config_vnc_hostname"),
            self.config_vnc_tls_secret == "" and msg.append("no config_vnc_tls_secret")
        ]):
            return False, Exception("\n".join(msg))
        else:
            return True, None
