import json
from typing import Optional, Tuple, Type, TypeVar
import http

from src.components import errors
from src.components.types import ResponseBaseModel
from .wrappers import wrapped_model_response

T = TypeVar('T')
E = TypeVar('E', bound=ResponseBaseModel)


def unmarshal_json_request(
        request,
        request_type: Type[T],
        err_response_type: Type[E]
) -> Tuple[Optional[Type[T]], Optional[Type[E]], Optional[Exception]]:
    """
    Check the request object is a sanic request object.

    returns: [parsed request object, error response, exception]
    """
    if request.json is None:
        return None, wrapped_model_response(
            err_response_type(
                status=http.HTTPStatus.BAD_REQUEST,
                message=str(errors.invalid_request_body)
            ),
            status_code=http.HTTPStatus.BAD_REQUEST
        ), Exception(errors.invalid_request_body),
    else:
        try:
            req = request_type(**request.json)
        except Exception as e:
            return None, wrapped_model_response(
                err_response_type(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ),
                status_code=http.HTTPStatus.BAD_REQUEST
            ), e
        return req, None, None
    pass


def unmarshal_query_args(
        request,
        request_type: Type[T],
        err_response_type: Type[E]
) -> Tuple[Optional[Type[T]], Optional[Type[E]], Optional[Exception]]:
    """
    Check the request object is a sanic request object.

    returns: [parsed request object, exception]

    """
    # parse query args
    if request.query_args is None:
        try:
            req = request_type()
        except Exception as e:
            return None, wrapped_model_response(
                err_response_type(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ),
                status_code=http.HTTPStatus.BAD_REQUEST
            ), e
    else:
        try:
            req = request_type(**{k: v for (k, v) in request.query_args})
        except Exception as e:
            return None, wrapped_model_response(
                err_response_type(
                    status=http.HTTPStatus.BAD_REQUEST,
                    message=str(e)
                ),
                status_code=http.HTTPStatus.BAD_REQUEST
            ), e

    return req, None, None


def unmarshal_mongodb_filter(query_filter: str) -> Tuple[Optional[dict], Optional[Exception]]:
    if query_filter != "":
        try:
            query_filter = json.loads(query_filter)
        except json.JSONDecodeError:
            return None, errors.wrong_query_filter
    else:
        query_filter = {}
    return query_filter, None
