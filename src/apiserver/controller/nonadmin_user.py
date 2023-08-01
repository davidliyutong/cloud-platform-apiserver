import http

from loguru import logger
from sanic import Blueprint
from sanic.response import json as json_response
from sanic_ext import openapi
from sanic_jwt import protected

import src.components.authz as authn
from src.apiserver.service import get_root_service
from src.components import errors
from .types import *

bp = Blueprint("nonadmin_user", url_prefix="/users", version=1)


@bp.get("/<username:str>", name="nonadmin_user_get")
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserGetResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def get(request, username: str):
    logger.debug(f"{request.path} invoked")

    if username is None or username == "":
        return json_response(
            UserGetResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        if username != request.ctx.user['username']:
            return json_response(
                PodGetResponse(
                    status=http.HTTPStatus.UNAUTHORIZED,
                    message="cannot get other users"
                ).model_dump(),
                status=http.HTTPStatus.UNAUTHORIZED
            )
        req = UserGetRequest(username=username)
        user, err = await get_root_service().user_service.get(request.app, req)
        if err is not None:
            return json_response(
                UserGetResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                UserGetResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )


@bp.put("/<username:str>", name="nonadmin_user_update")
@openapi.definition(
    body={'application/json': UserUpdateRequest.model_json_schema()},
)
@openapi.parameter("Authorization", str, location="header", required=True)
@openapi.response(200, {"application/json": UserUpdateResponse.model_json_schema()})
@protected()
@authn.validate_role()
async def update(request, username: str):
    logger.debug(f"{request.path} invoked")

    body = request.json
    if username is None or username == "":
        return json_response(
            UserUpdateResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ).model_dump(),
            status=http.HTTPStatus.BAD_REQUEST
        )
    else:
        if username != request.ctx.user['username']:
            return json_response(
                PodGetResponse(
                    status=http.HTTPStatus.UNAUTHORIZED,
                    message="cannot get other users"
                ).model_dump(),
                status=http.HTTPStatus.UNAUTHORIZED
            )

        body.update({"username": username})
        req = UserUpdateRequest(**body)
        user, err = await get_root_service().user_service.update(request.app, req)
        if err is not None:
            return json_response(
                UserUpdateResponse(
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=str(err)
                ).model_dump(),
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            return json_response(
                UserUpdateResponse(
                    status=http.HTTPStatus.OK,
                    message="success",
                    user=user
                ).model_dump(),
                status=http.HTTPStatus.OK
            )
