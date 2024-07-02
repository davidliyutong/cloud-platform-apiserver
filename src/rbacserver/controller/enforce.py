"""
This module implements the admin template controller.
"""

import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

from src.components.types import EnforceRequest, EnforceResponse, ResponseBaseModel
from src.components.utils import unmarshal_json_request, wrapped_model_response

bp = Blueprint("enforce", url_prefix="/enforce", version=1)


@bp.post("/", name="enforce_post")
@openapi.definition(
    body={'application/json': EnforceRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': EnforceResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
)
async def enforce(request):
    """
    Enforce the request against the policy and model, return the result.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # req: EnforceRequest
    req, error_resp, err = unmarshal_json_request(request, EnforceRequest, ResponseBaseModel)
    if err is not None:
        return error_resp

    # fire the enforce request
    result = request.app.ctx.enforcer.enforce(req.subject, req.object, req.action)
    logger.debug(f"enforce result: {result}")

    # return response
    return wrapped_model_response(
        EnforceResponse(status=http.HTTPStatus.OK, message="", result=result),
    )

from sanic_ext import openapi
openapi.component(EnforceRequest)
openapi.component(EnforceResponse)