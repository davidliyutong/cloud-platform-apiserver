from sanic import Blueprint
from sanic.response import text

bp = Blueprint("auth", url_prefix="/auth", version=1)


@bp.post("/basic", name="auth_basic", version=1)
async def basic(request):
    print(request)
    return text("NotImplementedError")
