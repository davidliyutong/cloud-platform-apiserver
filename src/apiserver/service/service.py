import dataclasses
from .common import ServiceInterface
from .admin_user import AdminUserService

@dataclasses.dataclass
class RootService:
    auth_basic_service: ServiceInterface = None
    admin_user_service: AdminUserService = None
    admin_template_service: ServiceInterface = None
    nonadmin_user_service: ServiceInterface = None
    nonadmin_pod_service: ServiceInterface = None


service = RootService(
    admin_user_service=AdminUserService(),
)
