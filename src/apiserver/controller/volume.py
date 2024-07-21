from sanic import Blueprint


bp = Blueprint("volume", url_prefix="/volumes", version=1)


@bp.get("/", name="project_volumes_list")
def list_volumes(request):
    """
    List all volumes in a project.
    """
    raise NotImplementedError


@bp.post("/", name="project_volumes_create")
def create_volume(request):
    """
    Create a new volume in a project.
    """
    raise NotImplementedError


@bp.get("/<volume_uuid:str>", name="project_volume_get")
def get_volume(request, volume_uuid: str):
    """
    Get a volume in a project.
    """
    raise NotImplementedError


@bp.put("/<volume_uuid:str>", name="project_volume_update")
def update_volume(request, volume_uuid: str):
    """
    Update a volume in a project.
    """
    raise NotImplementedError


@bp.delete("/<volume_uuid:str>", name="project_volume_delete")
def delete_volume(request, volume_uuid: str):
    """
    Delete a volume in a project.
    """
    raise NotImplementedError


# this is a workaround to register the bp
_unused = None
