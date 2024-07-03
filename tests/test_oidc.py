from typing import Optional, Tuple

from loguru import logger
from sanic import Sanic, response

# App
app = Sanic("OAuthApp")

from src.apiserver.controller.auth.oidc import OAuth2Config, AsyncOauthClient

from src.components.utils import UserFilter


def create_or_login(request, user_info: dict) -> Tuple[Optional[str], Optional[Exception]]:
    _f: UserFilter = request.app.ctx.oauth_user_filter
    if all([
        _f(user_info),
    ]):
        #   pseudo code
        #
        #   user, err = get_root_service().user_service.repo.get(user_info.account)
        #   if err is not None:
        #       user, err = CREATE_USER_FROM_OIDC(user_info) // with default quota, maybe
        #
        #   jwt, err = GENERATE_JWT_TOKEN(user)
        #   if err is not None:
        #       return None, err
        #   else:
        #       return jwt, None
        return ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjkzMjA3NjY3LCJpYXQiOjE2OTMy"
                "MDQwNjcsImVtYWlsIjpudWxsLCJyb2xlIjoic3VwZXJfYWRtaW4iLCJ1aWQiOjB9.hUqc4aXFeH3Vy7Y9QQSCrCqsxh81Zpaid7Bj"
                "spMzNJM"), None
    else:
        return None, Exception("user not allowed")


@app.route("/")
async def index(request):
    c: OAuth2Config = request.app.ctx.oauth_cfg
    return response.redirect(cfg.authorization_redirect_url)


"""
scope=email+openid+profile
"""


@app.route("/auth")
async def auth(request):
    logger.debug("/auth invoked")
    c: AsyncOauthClient = request.app.ctx.oauth_client

    # fetch token with authorization code
    oauth_token, err = await c.fetch_token(request.args.get("code"))
    # oauth_token, err = await c.refresh_token(oauth_token)
    if err is not None:
        return response.text("Authorization Error", 400)

    # fetch user info with access token
    user_info, err = await c.fetch_user(oauth_token)
    if err is not None:
        return response.text("Authorization Error", 400)
    # logger.debug(f"id_payload: {oauth_token.id_payload}")
    # logger.debug(f"user: {user_info}")

    # create or login
    jwt, err = create_or_login(request, user_info)
    if err is not None:
        return response.text("Authorization Error", 400)
    else:
        return response.json({"jwt": jwt}, 200)


# def test_user_filter():
#     f1 = UserFilter(mongo_like_filter_str='{"organize.id": 9}')
#     f2 = UserFilter(mongo_like_filter_str='{}')
#     print(f1.filter({"organize": {"id": 9}}))
#     print(f1.filter({"organize": {"id": 10}}))
#     print(f1.filter({}))
#
#     print(f2.filter({"organize": {"id": 9}}))
#     print(f2.filter({"organize": {"id": 10}}))
#     print(f2.filter({}))
#     return None


if __name__ == "__main__":
    cfg = OAuth2Config(name="cloud-platform",
                       base_url="https://authentik.davidliyutong.top/application/o",
                       client_id="d14422597a6ea8a9467bf016a46d7f1fae9b0ea7",
                       client_secret="3517fe860cd2457aaf843b219f52125433fb630b71b5306aaf0ddf1c932460065009cade59927324b830bcc32a4d0af1275be427c1639a8965396b1689ce3886",
                       redirect_url="http://127.0.0.1:8000/auth",
                       scope=["email", "openid", "profile"])

    client: AsyncOauthClient = cfg.get_async_client()
    user_filter = UserFilter(mongo_like_filter_str='{"$and": [{"organize.id": 26}, {"status": "正常"}]}')
    app.ctx.oauth_cfg = cfg
    app.ctx.oauth_client = client
    app.ctx.oauth_user_filter = user_filter
    app.run(host="localhost", port=8000, single_process=True)

