"""
This module implements the admin template controller.
"""

import http

from loguru import logger
from sanic import Blueprint
from sanic_ext import openapi

from src.components.types import ResponseBaseModel
from src.components.datamodels.rbac import RBACPolicyExchangeModelV2
from src.components.utils.wrappers import wrapped_model_response
from src.components.utils.checkers import unmarshal_json_request
from src.rbacserver.datamodels import UpdateNotificationMsg

bp = Blueprint("policy", url_prefix="/policy", version=1)


@bp.post("/reload", name="policy_reload")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': ResponseBaseModel.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[],
    description="Reload the policy from the database."
)
async def reload_policy(request):
    """
    Reload the policy from the database.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    try:
        if request.app.ctx.opt.rbac_num_workers > 1:
            request.app.shared_ctx.update_notification_queue.put_nowait(UpdateNotificationMsg(
                sender_id=request.app.m.name,
                processed_flag=0,
                sync_required=True,
            ))
        return wrapped_model_response(
            ResponseBaseModel(status=http.HTTPStatus.OK, message="success"),
        )

    except Exception as err:
        return wrapped_model_response(
            ResponseBaseModel(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err)),
        )


@bp.post("/add", name="policy_add")
@openapi.definition(
    body={'application/json': RBACPolicyExchangeModelV2.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': ResponseBaseModel.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[],
    description="Add new policies, sync them across workers, will not modify the database."
)
async def add_policy(request):
    """
    Add a raw policy to enforcer cache
    """
    logger.debug(f"{request.method} {request.path} invoked")

    req, error_resp, err = unmarshal_json_request(request, RBACPolicyExchangeModelV2, ResponseBaseModel)
    if err is not None:
        return error_resp

    if request.app.ctx.opt.rbac_num_workers > 1:
        request.app.shared_ctx.update_notification_queue.put_nowait(UpdateNotificationMsg(
            sender_id=request.app.m.name,
            processed_flag=0,
            sync_required=False,
            policies=req.policies
        ))

    # return response
    return wrapped_model_response(
        ResponseBaseModel(status=http.HTTPStatus.OK, message="success")
    )


openapi.component(RBACPolicyExchangeModelV2)
openapi.component(ResponseBaseModel)
