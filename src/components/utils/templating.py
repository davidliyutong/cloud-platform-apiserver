import json
import re
from typing import Optional, Dict, Any, Tuple, List

import mongoquery


def render_template_str(template_str: str,
                        kv: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], List[str], Optional[Exception]]:
    """
    Render template string with key-value pairs. The template string is in the format of ${{ key }}.
    """

    used_keys = []

    def replace(match):
        key = match.group(1)
        if key not in kv.keys():
            value = '${{ ' + key + ' }}'  # 保留原始的 ${{ key }}
        else:
            used_keys.append(key)
            value = str(kv.get(key, ''))
        return value  # 使用 kv 字典中的值替换

    if kv is not None:
        pattern = r'\$\{\{\s*(\w+)\s*\}\}'  # 匹配 ${{ key }}
        template_str = re.sub(pattern, replace, template_str)

    return template_str, list(set(used_keys)), None


class UserFilter:
    """
    User filter, use mongodb like filter string to filter allowed users
    """
    mongo_like_filter_str: Optional[str] = None  # e.g. {"username": "admin"}
    _mongo_like_filter: mongoquery.Query

    def __init__(self, mongo_like_filter_str: str = None):
        """
        Init user filter
        """
        self.mongo_like_filter_str = mongo_like_filter_str
        if self.mongo_like_filter_str is not None:
            self._mongo_like_filter = mongoquery.Query(json.loads(self.mongo_like_filter_str))
        else:
            self._mongo_like_filter = mongoquery.Query({})

    def filter(self, user_info: dict) -> bool:
        return self._mongo_like_filter.match(user_info)
