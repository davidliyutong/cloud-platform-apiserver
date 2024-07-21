from sanic import Blueprint

bp = Blueprint("pod", url_prefix="/pods", version=1)


@bp.get("/<project_uuid:str>/pods/", name="project_pods_list")
def list_project_pods(request, project_uuid):
    """
    List all pods in a project.
    """
    raise NotImplementedError


@bp.post("/<project_uuid:str>/pods/", name="project_pods_create")
def create_project_pods(request, project_uuid):
    """
    Create a new pod in a project.
    """
    raise NotImplementedError


@bp.get("/<project_uuid:str>/pods/<pod_uuid:str>", name="project_pod_get")
def get_project_pod(request, project_uuid: str, pod_uuid: str):
    """
    Get a pod in a project.
    """
    raise NotImplementedError


@bp.put("/<project_uuid:str>/pods/<pod_uuid:str>", name="project_pod_update")
def update_project_pod(request, project_uuid: str, pod_uuid: str):
    """
    Update a pod in a project.
    """
    raise NotImplementedError


@bp.delete("/<project_uuid:str>/pods/<pod_uuid:str>", name="project_pod_delete")
def delete_project_pod(request, project_uuid: str, pod_uuid: str):
    """
    Delete a pod in a project.
    """
    raise NotImplementedError

# this is a workaround to register the bp
_unused = None