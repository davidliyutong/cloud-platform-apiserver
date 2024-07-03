import base64
from typing import Optional, Tuple

from src.components import errors


def parse_bearer(bearer_str: Optional[str]) -> Tuple[Optional[str], Optional[Exception]]:
    """
    Parse bearer auth header
    """
    if bearer_str is None or len(bearer_str) == 0:
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
