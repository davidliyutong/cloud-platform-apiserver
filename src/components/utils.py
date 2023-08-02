import base64
from functools import wraps
from typing import Optional, Dict, Any, Tuple, List
import re
from kubernetes import client

from src.components import errors


def singleton(cls):
    """
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
    parse bearer auth header
    """
    if len(bearer_str) == 0 or bearer_str is None:
        return None, errors.header_missing
    authorization_header_split = bearer_str.split(' ')
    if len(authorization_header_split) != 2:
        return None, errors.header_malformed

    return authorization_header_split[1], None


def parse_basic(basic_str: Optional[str]) -> Tuple[Optional[Tuple[str, str]], Optional[Exception]]:
    """
    parse basic auth header
    """
    basic_auth_split = basic_str.split(' ')
    if len(basic_auth_split) < 2:
        return None, errors.header_malformed
    basic_auth = str(base64.b64decode(basic_auth_split[-1]), encoding='utf-8')
    username_password = basic_auth.split(':')
    if len(username_password) < 2:
        return None, errors.header_malformed

    return tuple(*username_password), None
