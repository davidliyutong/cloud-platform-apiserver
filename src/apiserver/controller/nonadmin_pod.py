from sanic import Blueprint
from sanic.response import text

bp = Blueprint("nonadmin_pod", url_prefix="/pod", version=1)


@bp.get("/<pod_id:str>", name="pod_get")
async def get(request):
    return text("NotImplementedError")


@bp.post("/<pod_id:str>", name="pod_create")
async def create(request):
    return text("NotImplementedError")


@bp.put("/<pod_id:str>", name="pod_update")
async def update(request):
    return text("NotImplementedError")


@bp.delete("/<pod_id:str>", name="pod_delete")
async def delete(request):
    return text("NotImplementedError")
