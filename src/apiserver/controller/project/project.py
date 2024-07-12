"""
This module implements the project controller.
"""
import http

from loguru import logger
from sanic_ext import openapi

import src.components.errors as errors
from src.apiserver.service import RootService
from src.components.auth.common import JWT_TOKEN_NAME
from src.components.types.project import (
    ProjectListRequest, ProjectListByUserRequest, ProjectListResponse,
    ProjectCreateRequest, ProjectCreateResponse,
    ProjectGetRequest, ProjectGetResponse,
    ProjectUpdateRequest, ProjectUpdateResponse,
    ProjectDeleteRequest, ProjectDeleteResponse
)
from src.components.utils.checkers import unmarshal_json_request, unmarshal_query_args
from src.components.utils.wrappers import wrapped_model_response
from src.components.auth import authn, authz
from .common import bp


@bp.get("/_/", name="project_list")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': ProjectListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[
        openapi.definitions.Parameter("skip", int, location="query", required=False),
        openapi.definitions.Parameter("limit", int, location="query", required=False),
        openapi.definitions.Parameter("extra_query_filter", str, location="query", required=False)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="list", resource_fmts=["resources::/projects/*"]
)
async def list_projects(request):
    """
    List all projects.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    req, err_resp, err = unmarshal_query_args(request, ProjectListRequest, ProjectListResponse)
    if err is not None:
        return err_resp

    # list projects
    count, res, err = await RootService().project_service.list(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            ProjectListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            ProjectListResponse(status=http.HTTPStatus.OK, message="success", total_projects=count, projects=res)
        )


@bp.get("/_/<username:str>", name="project_list_by_user")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': ProjectListResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    parameter=[
        openapi.definitions.Parameter("user_uuid", str, location="query", required=True),
        openapi.definitions.Parameter("skip", int, location="query", required=False),
        openapi.definitions.Parameter("limit", int, location="query", required=False),
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="list",
    resource_fmts=[
        "resources::/projects/*",
        "resources::/projects/.by_username/{username}/*"
    ]
)
async def list_user_projects(request, username: str):
    """
    List all projects accessible by a user.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse query args
    if username is None or username == "":
        return wrapped_model_response(
            ProjectListResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )

    # list user projects
    req = ProjectListByUserRequest(
        username=username,
        invoke_user_uuid=request.ctx.user_uuid,
        invoke_username=request.ctx.username
    )
    count, res, err = await RootService().project_service.list_by_user(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            ProjectListResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            ProjectListResponse(status=http.HTTPStatus.OK, message="success", total_projects=count, projects=res)
        )


@bp.post("/", name="project_create")
@openapi.definition(
    body={'application/json': ProjectCreateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': ProjectCreateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(action="create", resource_fmts=["resources::/projects/*"])
async def create_project(request):
    """
    Create a new project.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # parse request body
    req, err_resp, err = unmarshal_json_request(request, ProjectCreateRequest, ProjectCreateResponse)
    if err is not None:
        return err_resp

    # default owner_uuid to user_uuid
    if req.owner_uuid is None or req.owner_uuid == "":
        req.owner_uuid = request.ctx.user_uuid

    # create project
    if req.owner_uuid != request.ctx.user_uuid:
        # check permission for creating project for other user
        result = await RootService().policy_service.enforce(
            request.app,
            request.ctx.rbac_id, 'create', "resources::/projects/*"
        )
        if not result:
            return wrapped_model_response(
                ProjectCreateResponse(status=http.HTTPStatus.UNAUTHORIZED, message=str(errors.user_not_allowed))
            )

    res, err = await RootService().project_service.create(request.app, req)

    # return response
    if err is not None:
        return wrapped_model_response(
            ProjectCreateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
        )
    else:
        return wrapped_model_response(
            ProjectCreateResponse(status=http.HTTPStatus.OK, message="success", project=res)
        )


@bp.get("/<project_uuid:str>", name="project_get")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': ProjectGetResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="read", resource_fmts=[
        "resources::/projects/*",
        "resources::/projects/{project_uuid}",
    ]
)
async def get_project(request, project_uuid: str):
    """
    Get a project.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check project_uuid param in url
    if project_uuid is None or project_uuid == "":
        return wrapped_model_response(
            ProjectGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # get project
        req = ProjectGetRequest(project_uuid=project_uuid)
        res, err = await RootService().project_service.get(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                ProjectGetResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(err))
            )
        else:
            return wrapped_model_response(
                ProjectGetResponse(status=http.HTTPStatus.OK, message="success", project=res)
            )


@bp.put("/<project_uuid:str>", name="project_update")
@openapi.definition(
    body={'application/json': ProjectUpdateRequest.model_json_schema(ref_template="#/components/schemas/{model}")},
    response=[
        openapi.definitions.Response(
            {'application/json': ProjectUpdateResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="update",
    resource_fmts=[
        "resources::/projects/*",
        "resources::/projects/{project_uuid}",
    ]
)
async def update_project(request, project_uuid: str):
    """
    Update a project.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check project param in url
    if project_uuid is None or project_uuid == "":
        return wrapped_model_response(
            ProjectUpdateResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        req, err_resp, err = unmarshal_json_request(request, ProjectUpdateRequest, ProjectUpdateResponse)
        if err is not None:
            return err_resp

        req.project_uuid = project_uuid  # set project_id to request

        # update project
        res, err = await RootService().project_service.update(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                ProjectUpdateResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                ProjectUpdateResponse(status=http.HTTPStatus.OK, message="success", project=res)
            )


@bp.delete("/<project_uuid:str>", name="project_delete")
@openapi.definition(
    response=[
        openapi.definitions.Response(
            {'application/json': ProjectDeleteResponse.model_json_schema(ref_template="#/components/schemas/{model}")},
            status=200)
    ],
    secured={JWT_TOKEN_NAME: []}
)
@authn.protected()
@authz.enforce_rbac_any(
    action="delete",
    resource_fmts=[
        "resources::/projects/*",
        "resources::/projects/{project_uuid}",
    ]
)
async def delete_project(request, project_uuid: str):
    """
    Delete a project.
    """
    logger.debug(f"{request.method} {request.path} invoked")

    # check project_uuid param in url
    if project_uuid is None or project_uuid == "":
        return wrapped_model_response(
            ProjectDeleteResponse(status=http.HTTPStatus.BAD_REQUEST, message=str(errors.invalid_request_body))
        )
    else:
        # delete project
        req = ProjectDeleteRequest(project_uuid=project_uuid)

        if req.force:
            result = await RootService().policy_service.enforce(
                request.app,
                request.ctx.rbac_id, 'delete', "resources::/projects/*"
            )
            if not result:
                return wrapped_model_response(
                    ProjectDeleteResponse(status=http.HTTPStatus.UNAUTHORIZED, message=str(errors.user_not_allowed))
                )

        res, err = await RootService().project_service.delete(request.app, req)

        # return response
        if err is not None:
            return wrapped_model_response(
                ProjectDeleteResponse(status=http.HTTPStatus.INTERNAL_SERVER_ERROR, message=str(err))
            )
        else:
            return wrapped_model_response(
                ProjectDeleteResponse(status=http.HTTPStatus.OK, message="success", project=res)
            )


openapi.component(ProjectGetRequest)
openapi.component(ProjectGetResponse)
openapi.component(ProjectListRequest)
openapi.component(ProjectListByUserRequest)
openapi.component(ProjectListResponse)
openapi.component(ProjectCreateRequest)
openapi.component(ProjectCreateResponse)
openapi.component(ProjectUpdateRequest)
openapi.component(ProjectUpdateResponse)
openapi.component(ProjectDeleteRequest)
openapi.component(ProjectDeleteResponse)

# this is a workaround to register the bp
_unused = None
