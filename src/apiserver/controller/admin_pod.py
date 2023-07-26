from sanic import Blueprint

bp = Blueprint("admin_pod", url_prefix="/admin/pods", version=1)


@bp.get("/", name="admin_pod_list")
async def list(request):
    pass


@bp.post("/", name="admin_pod_create")
async def create(request):
    pass


@bp.get("/<pod_id:str>", name="admin_pod_get")
async def get(request, pod_id: str):
    pass


@bp.put("/<pod_id:str>", name="admin_pod_update")
async def update(request):
    pass


@bp.delete("/<pod_id:str>", name="admin_pod_delete")
async def delete(request):
    pass
