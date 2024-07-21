from odmantic import AIOEngine

from src.apiserver.service import ServiceInterface


class VolumeService(ServiceInterface):
    def __init__(self, odm_engine: AIOEngine):
        super().__init__()
        self.repo = None
        self.engine = odm_engine
