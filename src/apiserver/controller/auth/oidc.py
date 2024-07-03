import http
import json
from typing import Tuple, Optional

import httpx
import jwt
import shortuuid
from jsonpath_ng import parse
from loguru import logger
from pydantic import BaseModel, model_validator
from sanic import Blueprint
from sanic.response import json as json_response
from sanic.response import redirect as redirect_response
from sanic_ext import openapi

from src.apiserver.service import RootService, UserService
from src.components import errors
from src.components.auth.common import POLICY_ACCESS_TOKEN_DURATION_SECOND
from src.components.config import APIServerConfig, OIDCConfig
from src.components.datamodels.group import GroupEnumInternal
from src.components.utils import UserFilter
from src.components.utils.wrappers import wrapped_model_response

bp = Blueprint("auth_oidc", url_prefix="/auth/oidc", version=1)

from src.components.types.common import ResponseBaseModel, OIDCStatusResponse
from src.components.types.user import UserCreateRequest, UserGetRequest


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


class OAuth2Config(OIDCConfig):
    """
    OAuth2 config, contains all parameters needed for OAuth2
    """
    _client: httpx.AsyncClient = None
    _user_filter_instance: UserFilter = None
    _username_expr: parse = None
    _email_expr: parse = None
    _state: str = shortuuid.uuid()

    @classmethod
    def from_oidc_config(cls, cfg: OIDCConfig):
        """
        Create OAuth2Config from APIServerConfig
        """
        return cls(
            **cfg.model_dump(by_alias=True)
        )

    @model_validator(mode="after")
    def set_urls(self):
        """
        This validator completes urls if they are not set
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
        return (f"{self.authorization_url}?"
                f"response_type={self.response_type}&"
                f"redirect_uri={self.redirect_url}&"
                f"state={self._state}&"
                f"client_id={self.client_id}&"
                f"scope={self.scope_delimiter.join(self.scope)}")

    def get_frontend_redirect_url(
            self, token: str = "", refresh_token: str = "", success: bool = False, message: str = "OK"
    ) -> str:
        """
        Get frontend redirect url, with parameters
        """
        return (f"{self.frontend_login_url}?"
                f"token={token}&"
                f"refresh_token={refresh_token}&"
                f"success={str(success).lower()}&"
                f"message={message}")

    def get_async_client(self):
        """
        Get AsyncOauthClient
        """
        return AsyncOauthClient(self)

    def get_user_filter_instance(self) -> Tuple[UserFilter, Optional[Exception]]:
        """
        Get UserFilter
        """
        if self._user_filter_instance is None:
            try:
                self._user_filter_instance = UserFilter(mongo_like_filter_str=self.user_filter)
            except Exception as e:
                logger.exception(e)
                self._user_filter_instance = UserFilter(mongo_like_filter_str=None)
                return self._user_filter_instance, errors.user_failed_to_parse
        return self._user_filter_instance, None

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
async def oidc_status(request):
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
async def oidc_login(request):
    """
    This handler redirect user to IdP login page
    """
    c: OAuth2Config = request.app.ctx.oauth_cfg
    return redirect_response(c.authorization_redirect_url)


async def create_or_login(
        app, cfg: OAuth2Config, user_info: dict
) -> Tuple[Optional[str], Optional[str], Optional[Exception]]:
    """
    This function checks if the user exists, if not, create user
    """
    _f: UserFilter
    _f, err = cfg.get_user_filter_instance()
    if all([
        _f(user_info),
    ]):
        # try parse username and email
        try:
            username_expr = cfg.get_user_expr_instance()
            username = username_expr.find(user_info)[0].value
        except Exception as e:
            logger.error(f"failed to parse username: {e}")
            return None, None, errors.user_failed_to_parse

        try:
            email_expr = cfg.get_email_expr_instance()
            email = email_expr.find(user_info)[0].value
        except Exception as e:
            logger.warning(f"failed to parse email: {e}")
            email = None

        # get a service
        srv: UserService = RootService().user_service

        # find user
        user, err = await srv.get(app, UserGetRequest(username=username))
        if err is not None:
            # create the user it not exists
            req = UserCreateRequest(
                username=username,
                group=GroupEnumInternal.default,
                password="",
                email=email,
                quota=None,
                extra_info=user_info
            )
            user, err = await srv.create(app, req, registration=True)
            if err is not None:
                return None, None, err
        else:
            # guest and admin and parked users are allowed to log in
            if user.group in [
                GroupEnumInternal.guest.value,
                GroupEnumInternal.parked.value
            ]:
                return None, None, errors.user_not_allowed

        # generate jwt token
        access_token, refresh_token, err = await RootService().auth_service.generate_oidc_token(user)
        if err is not None:
            return None, None, err
        else:
            return access_token, refresh_token, None
    else:
        return None, None, errors.user_not_allowed


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
        if opt.debug:
            return wrapped_model_response(
                ResponseBaseModel(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return redirect_response(
                cfg.get_frontend_redirect_url(
                    token="",
                    refresh_token="",
                    success=False,
                    message=str(err)
                )
            )

    # fetch user info with access token
    user_info, err = await c.fetch_user(oauth_token)
    if err is not None:
        return wrapped_model_response(
            ResponseBaseModel(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
        )

    # try to decode id_token
    logger.debug(f"id_payload: {oauth_token.id_payload}")

    # create or login
    access_token, refresh_token, err = await create_or_login(request.app, cfg, user_info)

    if err is not None:
        if opt.debug:
            return wrapped_model_response(
                ResponseBaseModel(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return redirect_response(
                cfg.get_frontend_redirect_url(success=False, message=str(err))
            )
    else:
        resp = redirect_response(
            cfg.get_frontend_redirect_url(token=access_token, refresh_token=refresh_token, success=True)
        )
        resp.add_cookie("access_token", access_token, max_age=POLICY_ACCESS_TOKEN_DURATION_SECOND)
        resp.add_cookie("refresh_token", refresh_token, max_age=POLICY_ACCESS_TOKEN_DURATION_SECOND)
        return resp


openapi.component(OIDCStatusResponse)
