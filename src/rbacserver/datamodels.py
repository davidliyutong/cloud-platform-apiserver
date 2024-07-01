from typing import List, Tuple, Union

from pydantic import BaseModel


class UpdateNotificationMsg(BaseModel):
    sender_id: str
    processed_flag: int
    policies: List[Union[Tuple[str, str, str], Tuple[str, str, str, str], List[str]]] = []
    sync_required: bool = False
