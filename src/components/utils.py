from functools import wraps
from typing import Optional, Dict, Any, Tuple, List
import re


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


def parse_template_str(template_str: str,
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
