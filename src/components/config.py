from pydantic import BaseModel
from vyper import Vyper
import argparse
from typing import List, Any, Tuple, Optional, Dict
import os
import os.path as osp
from loguru import logger
import yaml

CONFIG_HOME_PATH = os.path.expanduser('~')
CONFIG_CONFIG_NAME = "backend"
CONFIG_PROJECT_NAME = "clpl"
CONFIG_EVENT_QUEUE_NAME = "clpl_event_queue"
CONFIG_GLOBAL_COLLECTION_NAME = "clpl_global"
CONFIG_USER_COLLECTION_NAME = "clpl_users"
CONFIG_POD_COLLECTION_NAME = "clpl_pods"
CONFIG_TEMPLATE_COLLECTION_NAME = "clpl_templates"


class BackendConfig(BaseModel):
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

    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "admin"

    config_code_hostname: str = None
    config_code_tls_secret: str = None
    config_vnc_hostname: str = None
    config_vnc_tls_secret: str = None

    @logger.catch
    def from_dict(self, d: Dict[str, Any]):
        # >>> Define Values >>>
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

        self.bootstrap_admin_password = str(d["bootstrap"]["adminPassword"])
        self.bootstrap_admin_username = str(d["bootstrap"]["adminUsername"])

        self.config_code_hostname = str(d["config"]["code"]["hostname"])
        self.config_code_tls_secret = str(d["config"]["code"]["tlsSecret"])
        self.config_vnc_hostname = str(d["config"]["vnc"]["hostname"])
        self.config_vnc_tls_secret = str(d["config"]["vnc"]["tlsSecret"])
        # <<< Define Values <<<
        return self

    @logger.catch
    def from_vyper(self, v: Vyper):
        # >>> Define Values >>>
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

        self.bootstrap_admin_password = v.get_string("bootstrap.adminPassword")
        self.bootstrap_admin_username = v.get_string("bootstrap.adminUsername")

        self.config_code_hostname = v.get_string("config.code.hostname")
        self.config_code_tls_secret = v.get_string("config.code.tlsSecret")
        self.config_vnc_hostname = v.get_string("config.vnc.hostname")
        self.config_vnc_tls_secret = v.get_string("config.vnc.tlsSecret")
        # <<< Define Values <<<

        return self

    def to_dict(self):
        # >>> Define Values >>>
        return {
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
            "bootstrap": {
                "adminUsername": self.bootstrap_admin_username,
                "adminPassword": self.bootstrap_admin_password,
            },
            "config": {
                "code": {
                    "hostname": self.config_code_hostname,
                    "tlsSecret": self.config_code_tls_secret,
                },
                "vnc": {
                    "hostname": self.config_vnc_hostname,
                    "tlsSecret": self.config_vnc_tls_secret,
                }
            }
        }
        # <<< Define Values <<<

    def to_sanic_config(self):
        # >>> Define Values >>>
        return {
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
            "BOOTSTRAP_ADMIN_USERNAME": self.bootstrap_admin_username,
            "BOOTSTRAP_ADMIN_PASSWORD": self.bootstrap_admin_password,
            "CONFIG_CODE_HOSTNAME": self.config_code_hostname,
            "CONFIG_CODE_TLSSECRET": self.config_code_tls_secret,
            "CONFIG_VNC_HOSTNAME": self.config_vnc_hostname,
            "CONFIG_VNC_TLSSECRET": self.config_vnc_tls_secret,
        }
        # <<< Define Values <<<

    @classmethod
    def get_default_config(cls) -> Vyper:
        v = Vyper()
        _DEFAULT: cls = cls()

        # >>> Set Default Values >>>
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

        v.set_default("bootstrap.adminUsername", _DEFAULT.bootstrap_admin_username)
        v.set_default("bootstrap.adminPassword", _DEFAULT.bootstrap_admin_password)

        v.set_default("config.code.hostname", _DEFAULT.config_code_hostname)
        v.set_default("config.code.tlsSecret", _DEFAULT.config_code_tls_secret)
        v.set_default("config.vnc.hostname", _DEFAULT.config_vnc_hostname)
        v.set_default("config.vnc.tlsSecret", _DEFAULT.config_vnc_tls_secret)
        # <<< Set Default Values <<<

        return v

    @staticmethod
    def get_cli_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", type=str, help="config file path", default=None)

        # >>> Set Default Values >>>
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

        parser.add_argument("--bootstrap.adminUsername", type=str, help="bootstrap admin username")
        parser.add_argument("--bootstrap.adminPassword", type=str, help="bootstrap admin password")

        parser.add_argument("--config.code.hostname", type=str, help="config code hostname")
        parser.add_argument("--config.code.tlsSecret", type=str, help="config code tlsSecret")
        parser.add_argument("--config.vnc.hostname", type=str, help="config vnc hostname")
        parser.add_argument("--config.vnc.tlsSecret", type=str, help="config vnc tlsSecret")
        # <<< Set Default Values <<<

        return parser

    @classmethod
    def load_config(cls, argv: List[str]) -> Tuple[Vyper, Optional[Exception]]:
        parser = cls.get_cli_parser()
        args = parser.parse_args(argv)

        v = cls.get_default_config()
        v.set_config_name(CONFIG_CONFIG_NAME)
        v.set_config_type("yaml")
        v.add_config_path(f"/etc/{CONFIG_CONFIG_NAME}")
        v.add_config_path(osp.join(CONFIG_HOME_PATH, f".{CONFIG_CONFIG_NAME}"))
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

        v.bind_env("bootstrap.adminUsername")
        v.bind_env("bootstrap.adminPassword")

        v.bind_env("config.code.hostname")
        v.bind_env("config.code.tlsSecret")
        v.bind_env("config.vnc.hostname")
        v.bind_env("config.vnc.tlsSecret")
        # <<< Set Env Values <<<

        logger.debug(f"watcher config: {cls().from_vyper(v).to_dict()}")

        return v, None

    @classmethod
    def save_config(cls, v: Vyper, path: str = None) -> Optional[Exception]:
        if path is None:
            path = osp.join(CONFIG_HOME_PATH, f".{CONFIG_PROJECT_NAME}", f"{CONFIG_CONFIG_NAME}.yaml")

        _DIR = osp.dirname(path)
        if not osp.exists(_DIR):
            os.makedirs(_DIR, exist_ok=True)

        _VALUE = cls().from_vyper(v).to_dict()

        logger.debug(f"save path: {path}")
        logger.debug(f"save config: {_VALUE}")

        with open(path, "w") as f:
            yaml.dump(_VALUE, f, default_flow_style=False)

        return None
