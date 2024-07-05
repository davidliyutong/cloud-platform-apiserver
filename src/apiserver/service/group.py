from odmantic import AIOEngine

from src.apiserver.service import ServiceInterface


class GroupService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self.engine = odm_engine
