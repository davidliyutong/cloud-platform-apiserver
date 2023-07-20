from pydantic import BaseModel
from vyper import Vyper
import argparse
from typing import List, Any, Tuple, Optional, Dict, Union
import os
import os.path as osp
from loguru import logger
import yaml

_HOME = os.path.expanduser('~')
_CONFIG_CONFIG_NAME = "backend"
_CONFIG_PROJECT_NAME = "clpl"


class BackendConfig(BaseModel):
    api_num_workers: int = 4
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_access_log: bool = False

    db_host: str = "127.0.0.1"
    db_port: int = 27017
    db_username: str = _CONFIG_PROJECT_NAME
    db_password: str = _CONFIG_PROJECT_NAME
    db_database: str = _CONFIG_PROJECT_NAME

    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "admin"


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

        self.bootstrap_admin_password = str(d["bootstrap"]["adminPassword"])
        self.bootstrap_admin_username = str(d["bootstrap"]["adminUsername"])
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

        self.bootstrap_admin_password = v.get_string("bootstrap.adminPassword")
        self.bootstrap_admin_username = v.get_string("bootstrap.adminUsername")
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
            "bootstrap": {
                "adminUsername": self.bootstrap_admin_username,
                "adminPassword": self.bootstrap_admin_password,
            }
        }
        # <<< Define Values <<<

    def to_sanic_config(self):
        # >>> Define Values >>>
        return {
            "API_NUM_WORKERS": self.api_num_workers,
            "API_HOST": self.api_host,
            "API_PORT": self.api_port,
            "API_ACCESS_LOG": self.api_access_log,
            "DB_HOST": self.db_host,
            "DB_PORT": self.db_port,
            "DB_USERNAME": self.db_username,
            "DB_PASSWORD": self.db_password,
            "DB_DATABASE": self.db_database,
            "BOOTSTRAP_ADMIN_USERNAME": self.bootstrap_admin_username,
            "BOOTSTRAP_ADMIN_PASSWORD": self.bootstrap_admin_password
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

        v.set_default("bootstrap.adminUsername", _DEFAULT.bootstrap_admin_username)
        v.set_default("bootstrap.adminPassword", _DEFAULT.bootstrap_admin_password)
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

        parser.add_argument("--bootstrap.adminUsername", type=str, help="bootstrap admin username")
        parser.add_argument("--bootstrap.adminPassword", type=str, help="bootstrap admin password")
        # <<< Set Default Values <<<

        return parser

    @classmethod
    def load_config(cls, argv: List[str]) -> Tuple[Vyper, Optional[Exception]]:
        parser = cls.get_cli_parser()
        args = parser.parse_args(argv)

        v = cls.get_default_config()
        v.set_config_name(_CONFIG_CONFIG_NAME)
        v.set_config_type("yaml")
        v.add_config_path(f"/etc/{_CONFIG_CONFIG_NAME}")
        v.add_config_path(osp.join(_HOME, f".{_CONFIG_CONFIG_NAME}"))
        v.add_config_path(".")
        if args.config is not None:
            v.set_config_file(args.config)
        try:
            v.merge_in_config()
            logger.debug(f"load config form : {v._config_file}")
        except FileNotFoundError:
            v = cls.get_default_config()
            logger.warning(f"config file not found")

        v.set_env_prefix(_CONFIG_PROJECT_NAME.upper())
        v.set_env_key_replacer(".", "_")

        v.bind_args(vars(args))

        # >>> Set Env Values >>>
        v.bind_env("api.numWorker")
        v.bind_env("api.host")
        v.bind_env("api.port")
        v.bind_env("api.accessLog")

        v.bind_env("db.host")
        v.bind_env("db.port")
        v.bind_env("db.username")
        v.bind_env("db.password")
        v.bind_env("db.database")

        v.bind_env("bootstrap.adminUsername")
        v.bind_env("bootstrap.adminPassword")
        # <<< Set Env Values <<<

        logger.debug(f"watcher config: {cls().from_vyper(v).to_dict()}")

        return v, None

    @classmethod
    def save_config(cls, v: Vyper, path: str = None) -> Optional[Exception]:
        if path is None:
            path = osp.join(_HOME, f".{_CONFIG_PROJECT_NAME}", f"{_CONFIG_CONFIG_NAME}.yaml")

        _DIR = osp.dirname(path)
        if not osp.exists(_DIR):
            os.makedirs(_DIR, exist_ok=True)

        _VALUE = cls().from_vyper(v).to_dict()

        logger.debug(f"save path: {path}")
        logger.debug(f"save config: {_VALUE}")

        with open(path, "w") as f:
            yaml.dump(_VALUE, f, default_flow_style=False)

        return None
