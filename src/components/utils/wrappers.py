from sanic.response import json as json_response

from src.components.types import ResponseBaseModel


def wrapped_model_response(model: ResponseBaseModel, status_code: int = None, headers: dict = None):
    """
    Wrap the model response with status code.
    """
    return json_response(
        model.model_dump(),
        status=model.status if status_code is None else status_code,
        headers=headers
    )
