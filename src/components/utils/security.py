from hashlib import sha256
from typing import Union


def get_hashed_text(text: Union[str, bytes]) -> str:
    """
    Get hashed text.
    """
    return sha256(text.encode() if isinstance(text, str) else text).hexdigest()
