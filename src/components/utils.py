"""
This module contains all the utility functions.
"""

import base64
from functools import wraps
from typing import Optional, Dict, Any, Tuple, List
import re
import signal

from loguru import logger
from kubernetes import client

from src.components import errors


def singleton(cls):
    """
    Singleton decorator. Make sure only one instance of cls is created.

    :param cls: cls
    :return: instance
    """
    _instances = {}

    @wraps(cls)
    def instance(*args, **kw):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kw)
        return _instances[cls]

    return instance


def render_template_str(template_str: str,
                        kv: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], List[str], Optional[Exception]]:
    """
    Render template string with key-value pairs. The template string is in the format of ${{ key }}.
    """

    used_keys = []

    def replace(match):
        key = match.group(1)
        if key not in kv.keys():
            value = ''
        else:
            used_keys.append(key)
            value = str(kv.get(key, ''))
        return value  # 使用 kv 字典中的值替换

    if kv is not None:
        pattern = r'\$\{\{\s*(\w+)\s*\}\}'  # 匹配 ${{ key }}
        template_str = re.sub(pattern, replace, template_str)

    return template_str, used_keys, None


def get_k8s_client(host: str,
                   port: int,
                   ca_cert_path: str,
                   token_path: str,
                   verify_ssl: bool = False,
                   debug: bool = False) -> client:
    """
    Get Kubernetes client.
    """

    api_server = f"https://{host}:{str(port)}"
    ca_cert_path = ca_cert_path
    token_path = token_path
    with open(token_path, "r") as f:
        token = f.read()

    # Set the configuration
    configuration = client.Configuration()
    configuration.ssl_ca_cert = ca_cert_path
    configuration.host = api_server
    configuration.verify_ssl = verify_ssl
    configuration.debug = debug
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)

    return client


def parse_bearer(bearer_str: Optional[str]) -> Tuple[Optional[str], Optional[Exception]]:
    """
    Parse bearer auth header
    """
    if len(bearer_str) == 0 or bearer_str is None:
        return None, errors.header_missing
    authorization_header_split = bearer_str.split(' ')
    if len(authorization_header_split) != 2 or authorization_header_split[0] != 'Bearer':
        return None, errors.header_malformed

    return authorization_header_split[1], None


def parse_basic(basic_str: Optional[str]) -> Tuple[Optional[Tuple[str, str]], Optional[Exception]]:
    """
    Parse basic auth header
    """
    basic_auth_split = basic_str.split(' ')
    if len(basic_auth_split) != 2 or basic_auth_split[0] != 'Basic':
        return None, errors.header_malformed
    basic_auth = str(base64.b64decode(basic_auth_split[-1]), encoding='utf-8')
    username_password = basic_auth.split(':')
    if len(username_password) != 2:
        return None, errors.header_malformed

    return (username_password[0], username_password[1]), None


class DelayedKeyboardInterrupt:
    """
    Shield code from KeyboardInterrupt
    """
    signal_received = None

    def __enter__(self):
        self.signal_received = None
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logger.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)
