import base64

from hashlib import sha256
import secrets
from typing import Optional, Tuple, Any, Dict

import src.components.datamodels as datamodels
import src.components.errors as errors

from src.apiserver.repo import Repo
from sanic import request, response, Sanic
from sanic_jwt import Configuration, Responses, exceptions, Authentication
from loguru import logger


async def get_user(repo: Repo,
                   username: str) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
    db_col = repo.get_collection(datamodels.database_name, datamodels.user_collection_name)
    user = await db_col.find_one({"username": username})

    if user is None:
        return None, errors.user_not_found
    else:
        user_model = datamodels.UserModel(**user)
        return user_model.model_dump(), None


async def authenticate(req: request.Request):
    logger.debug(f"{req.path} invoked")
    username = req.json.get("username", None)
    password = req.json.get("password", None)

    if not username or not password:
        raise exceptions.AuthenticationFailed(str(errors.empty_username_or_password))

    user, err = await get_user(Repo(req.app.config), username)
    if user is None:
        raise exceptions.AuthenticationFailed(str(err))
    else:
        password_hashed = sha256(password.encode()).hexdigest()
        if secrets.compare_digest(
                password_hashed.encode('utf-8'),
                str(user["password"]).encode('utf-8')
        ):
            return user
        else:
            raise exceptions.AuthenticationFailed(errors.wrong_password)


class MyJWTConfig(Configuration):
    access_token_name = "token"

    authorization_header_prefix = "Bearer:"

    # -------------- url_prefix ---------------------
    # [描述] 获取授权的路由地址
    # [默认] '/auth'
    url_prefix = '/v1/auth/jwt'

    path_to_authenticate = '/login'
    path_to_refresh = '/refresh'

    # -------------- secret -------------------------
    # [描述] 加密密码
    # [默认] 'This is a big secret. Shhhhh'
    # [建议] 该密码是 JWT 的安全核心所在，需要保密，尽量使用更长更复杂的密码
    secret = base64.encodebytes(secrets.token_bytes(32))

    # -------------- expiration_delta ----------------------
    # [描述] 过期时间，单位为秒
    # [默认] 30 分钟，即：60 * 30
    # [建议] 该时间不宜过长，同时建议开启 refresh_token_enabled 以便自动更新 token
    expiration_delta = 60 * 60  # 改为 60 分钟过期

    # refresh_token_name = 'refresh_token'
    # refresh_token_enabled = True  # 开启 refresh_token 功能

    # -------------- cookie_set ---------------------
    # [描述] 是否将获取到的 token 信息写入到 cookie
    # [默认] False，即不写入cookie
    # 只有该项为 True，其它 cookie 相关设置才会起效。
    # cookie_set = True

    # -------------- cookie_access_token_name ---------------
    # [描述] cookie 中存储 token 的名称。
    # [默认] 'access_token'
    # cookie_access_token_name = "token"

    #  -------------- cookie_access_token_name ---------------
    # [描述] 包含用户 id 的用户对象的键或属性，这里对应 User 类的用户唯一标识
    # [默认] 'user_id'
    user_id = "username"

    refresh_token_enabled = True  # 开启 refresh_token 功能

    claim_iat = True  # 显示签发时间，JWT的默认保留字段，在 sanic-jwt 中默认不显示该项


class MyJWTAuthentication(Authentication):

    # 从 payload 中解析用户信息，然后返回查找到的用户
    # request: request
    # kwargs: payload
    async def retrieve_user(self, request, **kwargs):
        user_id_attribute = self.config.user_id()
        if 'payload' in kwargs.keys():
            user_id = kwargs['payload'].get(user_id_attribute)
            user, err = await get_user(Repo(request.app.config), user_id)
            if err is not None:
                raise exceptions.AuthenticationFailed(str(err))
            else:
                return user
        else:
            raise exceptions.AuthenticationFailed(str(errors.invalid_token))

    # 拓展 payload
    async def extend_payload(self, payload, *args, **kwargs):
        # 可以获取 User 中的一些属性添加到 payload 中
        # 注意：payload 信息是公开的，这里不要添加敏感信息
        user_id_attribute = self.config.user_id()
        user_id = payload.get(user_id_attribute)
        user, _ = await get_user(Repo(Sanic.get_app("root").config), user_id)
        payload.update({'email': user["email"], 'role': user['role'], 'uid': user['uid']})  # 比如添加性别属性
        return payload

    async def extract_payload(self, req, verify=True, *args, **kwargs):
        return await super().extract_payload(req, verify)


class MyJWTResponse(Responses):
    @staticmethod
    async def get_access_token_output(request, user, config, instance):
        access_token = await instance.ctx.auth.generate_access_token(user)

        output = {"description": "", "status": 200, "message": "success", config.access_token_name(): access_token}

        return access_token, output

    # 自定义发生异常的返回数据
    @staticmethod
    def exception_response(req: request.Request, exception: exceptions):
        # sanic-jwt.exceptions 下面定义的异常类型：
        # AuthenticationFailed
        # MissingAuthorizationHeader
        # MissingAuthorizationCookie
        # InvalidAuthorizationHeader
        # MissingRegisteredClaim
        # Unauthorized
        msg = str(exception)
        if exception.status_code == 500:
            msg = str(exception)
        elif isinstance(exception, exceptions.AuthenticationFailed):
            msg = str(exception)
        else:
            if "expired" in msg:
                msg = "authorization expired"
            else:
                msg = "unauthorized"
        result = {
            "code": exception.status_code,
            "msg": msg,
            "token": "",
        }
        return response.json(result, status=exception.status_code)


async def retrieve_refresh_token(request, user_id, *args, **kwargs):
    _ = f'refresh_token_{user_id}'
    token_str = request.json.get('refresh_token', None)
    if token_str is None:
        return b''
    else:
        return token_str.encode('utf-8')


async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
    _ = f'refresh_token_{user_id}'
    return
