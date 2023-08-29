import http
import json
from typing import Tuple, Optional, List

import httpx
from jsonpath_ng import parse
import jwt
import shortuuid
from loguru import logger
from pydantic import BaseModel, model_validator
from sanic import Blueprint
from sanic.response import json as json_response
from sanic.response import redirect as redirect_response
from sanic_ext import openapi

from src.components.config import APIServerConfig
from src.apiserver.service import get_root_service, UserService
from src.components import errors
from src.components.datamodels import UserRoleEnum, QuotaModel
from src.components.utils import UserFilter, random_password

bp = Blueprint("auth_oidc", url_prefix="/auth/oidc", version=1)

from .types import OIDCStatusResponse, ResponseBaseModel


class OAuthToken(BaseModel):
    """
    OAuth token model
    """
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    id_token: Optional[str] = None

    @property
    def id_payload(self) -> Optional[dict]:
        """
        Decode id_token, skip signature verification
        """
        if self.id_token is not None and self.id_token != "":
            return jwt.decode(self.id_token, options={"verify_signature": False})
        else:
            return None


class OAuth2Config(BaseModel):
    """
    OAuth2 config, contains all parameters needed for OAuth2
    """
    _client: httpx.AsyncClient = None
    _user_filter_instance: UserFilter = None
    _username_expr: parse = None
    _email_expr: parse = None

    name: str
    base_url: str
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    user_info_url: Optional[str] = None
    logout_url: Optional[str] = None
    jwks_url: Optional[str] = None
    frontend_login_url: Optional[str] = None
    client_id: str
    client_secret: str
    redirect_url: str
    scope: List[str] = ["openid"]
    scope_delimiter: str = "+"
    state: str = shortuuid.uuid()
    response_type: str = "code"
    grant_type: str = "authorization_code"
    user_filter: str = "{}"
    user_info_path: str = "$"
    username_path: str = "preferred_username"
    email_path: str = "email"

    @classmethod
    def from_apiserver_config(cls, cfg: APIServerConfig):
        """
        Create OAuth2Config from APIServerConfig
        """
        return cls(
            name=cfg.oidc_name,
            base_url=cfg.oidc_base_url,
            authorization_url=cfg.oidc_authorization_url,
            token_url=cfg.oidc_token_url,
            user_info_url=cfg.oidc_user_info_url,
            logout_url=cfg.oidc_logout_url,
            jwks_url=cfg.oidc_jwks_url,
            frontend_login_url=cfg.oidc_frontend_login_url,
            client_id=cfg.oidc_client_id,
            client_secret=cfg.oidc_client_secret,
            redirect_url=cfg.oidc_redirect_url,
            scope=cfg.oidc_scope,
            scope_delimiter=cfg.oidc_scope_delimiter,
            response_type=cfg.oidc_response_type,
            grant_type=cfg.oidc_grant_type,
            user_filter=cfg.oidc_user_filter,
            user_info_path=cfg.oidc_user_info_path,
            username_path=cfg.oidc_username_path,
            email_path=cfg.oidc_email_path
        )

    @model_validator(mode="after")
    def set_urls(self):
        """
        This validator completes urls
        """
        if self.authorization_url is None or self.authorization_url == "":
            self.authorization_url = f"{self.base_url}/authorize/"

        if self.token_url is None or self.token_url == "":
            self.token_url = f"{self.base_url}/token/"

        if self.user_info_url is None or self.user_info_url == "":
            self.user_info_url = f"{self.base_url}/userinfo/"

        if self.logout_url is None or self.logout_url == "":
            self.logout_url = f"{self.base_url}/{self.name}/end-session/"

        if self.jwks_url is None or self.jwks_url == "":
            self.jwks_url = f"{self.base_url}/{self.name}/jwks/"

        if self.frontend_login_url is None or self.frontend_login_url == "":
            self.frontend_login_url = f"{self.base_url}/login"

    @property
    def authorization_redirect_url(self):
        """
        Get authorization redirect url, with parameters
        """
        return f"{self.authorization_url}?response_type={self.response_type}&redirect_uri={self.redirect_url}&state={self.state}&client_id={self.client_id}&scope={self.scope_delimiter.join(self.scope)}"

    def get_frontend_redirect_url(self, token: str, refresh_token: str, success: bool) -> str:
        """
        Get frontend redirect url, with parameters
        """
        return f"{self.frontend_login_url}?token={token}&refresh_token={refresh_token}&success={str(success).lower()}"

    def get_async_client(self):
        """
        Get AsyncOauthClient
        """
        return AsyncOauthClient(self)

    def get_user_filter_instance(self):
        """
        Get UserFilter
        """
        if self._user_filter_instance is None:
            self._user_filter_instance = UserFilter(mongo_like_filter_str=self.user_filter)
        return self._user_filter_instance

    def get_user_expr_instance(self):
        """
        Get User expression
        """
        if self._username_expr is None:
            self._username_expr = parse(self.username_path)
        return self._username_expr

    def get_email_expr_instance(self):
        """
        Get email expression
        """
        if self._email_expr is None:
            self._email_expr = parse(self.email_path)
        return self._email_expr


class AsyncOauthClient:
    """
    AsyncOauthClient is a client for OAuth2 that uses httpx to accomplish operations
    """

    def __init__(self, cfg: OAuth2Config):
        self._cfg = cfg
        self._client = httpx.AsyncClient()
        self._oauth_token = None  # cached oauth token
        self._public_keys = None  # cached public keys

        self._user_info_expr = parse(self._cfg.user_info_path)

    async def fetch_token(self, code: str) -> Tuple[Optional[OAuthToken], Optional[Exception]]:
        """
        Fetch token with authorization code from token endpoint
        """
        _headers = {
            "accept": "application/json"
        }

        # call endpoint
        res = await self._client.post(
            self._cfg.token_url,
            headers=_headers,
            auth=(self._cfg.client_id, self._cfg.client_secret),
            data={
                "grant_type": self._cfg.grant_type,
                "client_id": self._cfg.client_id,
                "client_secret": self._cfg.client_secret,
                "code": code,
                "redirect_uri": self._cfg.redirect_url
            }
        )

        # parse token
        if res.status_code == http.HTTPStatus.OK:
            oauth_token = OAuthToken(**res.json())
            self._oauth_token = oauth_token
            return oauth_token, None
        else:
            return None, Exception("Authorization Error")

    async def refresh_token(self, oauth_token: OAuthToken = None) -> Tuple[Optional[OAuthToken], Optional[Exception]]:
        """
        Refresh token with refresh token from token endpoint, use the cached oauth_token if not provided
        """
        if oauth_token is None:
            oauth_token = self._oauth_token

        _headers = {
            "accept": "application/json"
        }

        # call endpoint
        res = await self._client.post(
            self._cfg.token_url,
            headers=_headers,
            auth=(self._cfg.client_id, self._cfg.client_secret),
            data={
                "grant_type": "refresh_token",
                "client_id": self._cfg.client_id,
                "client_secret": self._cfg.client_secret,
                "refresh_token": oauth_token.refresh_token,
                "redirect_uri": self._cfg.redirect_url
            }
        )

        # parse token
        if res.status_code == http.HTTPStatus.OK:
            oauth_token = OAuthToken(**res.json())
            self._oauth_token = oauth_token
            return oauth_token, None
        else:
            return None, Exception("Authorization Error")

    async def fetch_user(self, oauth_token: OAuthToken = None) -> Tuple[Optional[dict], Optional[Exception]]:
        """
        Fetch user info with access token from user info endpoint, use the cached oauth_token if not provided
        """
        if oauth_token is None:
            oauth_token = self._oauth_token

        # Get user info from Authentik using the access token
        _headers = {"Authorization": f"Bearer {oauth_token.access_token}"}
        res = await self._client.get(self._cfg.user_info_url, headers=_headers)
        try:
            res.raise_for_status()
        except Exception as e:
            return None, e
        user_payload = res.json()
        logger.debug(f"user_payload(raw): {user_payload}")
        user_info = self._user_info_expr.find(user_payload)[0].value

        return user_info, None

    async def fetch_public_keys(self) -> Tuple[Optional[dict], Optional[Exception]]:
        """
        Fetch public keys from jwks endpoint
        """
        # call endpoint
        res = await self._client.get(self._cfg.jwks_url)
        try:
            res.raise_for_status()
        except Exception as e:
            return None, e

        # decode jwks response
        public_keys = {}
        jwks = res.json()
        for jwk in jwks['keys']:
            kid = jwk['kid']
            public_keys[kid] = jwt.get_algorithm_by_name('RSAAlgorithm').from_jwk(json.dumps(jwk))

        self._public_keys = public_keys
        return public_keys, None

    async def validate_token(self, token: str) -> Tuple[Optional[dict], Optional[Exception]]:
        if self._public_keys is None:
            await self.fetch_public_keys()

        try:
            kid = jwt.get_unverified_header(token)['kid']
            key = self._public_keys[kid]
            payload = jwt.decode(token, key=key, algorithms=['RS256'])
        except Exception as e:
            return None, e
        return payload, None


@bp.get("/status", name="status", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {"application/json": OIDCStatusResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200
        )
    ]
)
def oidc_status(request):
    if request.app.ctx.oauth_cfg is None:
        return json_response(None)
    else:
        response = OIDCStatusResponse(
            name=request.app.ctx.oauth_cfg.name,
            path=request.app.url_for("root.auth_oidc.login")  # "/v1/auth/oidc/login"
        )
        return json_response(response.model_dump())


@bp.get("/login", name="login", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            status=302,
            description="redirect to authorization url"
        )
    ]
)
def oidc_login(request):
    c: OAuth2Config = request.app.ctx.oauth_cfg
    return redirect_response(c.authorization_redirect_url)


async def create_or_login(cfg: OAuth2Config, user_info: dict) -> Tuple[Optional[str], Optional[Exception]]:
    _f: UserFilter = cfg.get_user_filter_instance()
    if all([
        _f.filter(user_info),
    ]):
        # try parse username and email
        try:
            username_expr = cfg.get_user_expr_instance()
            username = username_expr.find(user_info)[0].value
        except Exception as e:
            logger.error(f"failed to parse username: {e}")
            return None, errors.user_failed_to_parse

        try:
            email_expr = cfg.get_email_expr_instance()
            email = email_expr.find(user_info)[0].value
        except Exception as e:
            logger.warning(f"failed to parse email: {e}")
            email = None

        # get a service
        srv: UserService = get_root_service().user_service

        # find user
        user, err = await srv.repo.get(username)
        if err is not None:
            # create the user it not exists
            user, err = await srv.repo.create(username=username,
                                              password=random_password(),
                                              email=email,
                                              role=UserRoleEnum.user,
                                              quota=QuotaModel.default_quota(),
                                              extra_info=user_info)
            if err is not None:
                return None, err
        else:
            # super_admin is not allowed to log in
            if user.role in ['super_admin']:
                return None, errors.user_not_allowed

        # generate jwt token
        access_token, err = await get_root_service().auth_service.generate_jwt_token(user)
        if err is not None:
            return None, err
        else:
            return access_token, None
    else:
        return None, errors.user_not_allowed


@bp.get("/authorize", name="authorize", version=1)
@openapi.definition(
    response=[
        openapi.definitions.Response(
            status=302,
            description="redirect to authorization url"
        ),
        openapi.definitions.Response(
            status=400,
            description="Authorization Error"
        )
    ]
)
async def oidc_authorize(request):
    """
    This endpoint is called by identity provider after user login, will redirect to frontend login page with token
    """
    logger.debug(f"{request.method} {request.path} invoked")
    c: AsyncOauthClient = request.app.ctx.oauth_client
    cfg: OAuth2Config = request.app.ctx.oauth_cfg
    opt: APIServerConfig = request.app.ctx.opt

    # fetch token with authorization code
    oauth_token, err = await c.fetch_token(request.args.get("code"))
    # oauth_token, err = await c.refresh_token(oauth_token)
    if err is not None:
        return json_response(
            ResponseBaseModel(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(err),
                description="Authorization Error"
            ).model_dump(), status=http.HTTPStatus.BAD_REQUEST
        )

    # fetch user info with access token
    user_info, err = await c.fetch_user(oauth_token)
    if err is not None:
        return json_response(
            ResponseBaseModel(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(err),
                description="Authorization Error"
            ).model_dump(), status=http.HTTPStatus.BAD_REQUEST
        )

    # try to decode id_token
    logger.debug(f"id_payload: {oauth_token.id_payload}")

    # create or login
    access_token, err = await create_or_login(cfg, user_info)

    if err is not None:
        if opt.debug:
            return json_response(
                ResponseBaseModel(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(err),
                    description="Authorization Error"
                ).model_dump(), status=http.HTTPStatus.BAD_REQUEST
            )
        else:
            return redirect_response(
                cfg.get_frontend_redirect_url(
                    token="",
                    refresh_token="",
                    success=False
                )
            )
    else:
        # attention: this refresh token is generated according to :
        # https://sanic-jwt.readthedocs.io/en/latest/pages/refreshtokens.html
        refresh_token = random_password(24)
        return redirect_response(
            cfg.get_frontend_redirect_url(
                token=access_token,
                refresh_token=refresh_token,
                success=True
            )
        )
        # return json_response({"jwt": access_token}, http.HTTPStatus.OK)
