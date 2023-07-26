from sanic import Blueprint
from sanic.response import text

bp = Blueprint("nonadmin_user", url_prefix="/user", version=1)


@bp.get("/<username>", name="user_get")
async def get(request):
    return text("NotImplementedError")


@bp.put("/<username>", name="user_update")
async def update(request):
    return text("NotImplementedError")
