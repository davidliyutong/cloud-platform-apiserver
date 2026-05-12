"""
This module contains all the errors that can be raised by the application.
"""
import http

db_connection_error = Exception("db connection error")
duplicate_username = Exception("duplicate username")
empty_username_or_password = Exception("empty username or password")
header_malformed = Exception("header malformed")
header_missing = Exception("header missing")
invalid_request_body = Exception("invalid request body")
invalid_token = Exception("invalid token")
k8s_config_not_found = Exception("Kubernetes config not found")
k8s_failed_to_create = Exception("Kubernetes failed to create")
k8s_failed_to_delete = Exception("Kubernetes failed to delete")
k8s_failed_to_get = Exception("Kubernetes failed to get")
k8s_failed_to_list = Exception("Kubernetes failed to list")
k8s_failed_to_update = Exception("Kubernetes failed to update")
k8s_timeout = Exception("Kubernetes timeout")
k8s_pod_failed = Exception("Kubernetes pod failed to reach target status")
old_password_required = Exception("old password required")
pod_not_found = Exception("pod not found")
pod_not_stopped = Exception("pod must be stopped to edit its specs")
quota_exceeded = Exception("quota exceeded")
template_invalid = Exception("template invalid")
template_key_not_exists = BaseException("template key not exists")
template_key_not_used = Exception("template key not used")
template_not_found = Exception("template not found")
unknown_error = Exception("unknown error")
user_not_found = Exception("user not found")
user_not_allowed = Exception("user not allowed")
user_failed_to_parse = Exception("user failed to parse")
username_required = Exception("username required")
wrong_password = Exception("wrong password")
wrong_pod_profile = Exception("wrong pod profile")
wrong_query_filter = Exception("wrong query filter")
wrong_template_profile = Exception("wrong template profile")
wrong_user_profile = Exception("wrong user profile")


# Errors that are caused by the user's request and should surface as HTTP 4xx.
# Anything not in this mapping falls back to 500 in the controllers.
USER_ERROR_HTTP_STATUS = {
    id(pod_not_stopped): http.HTTPStatus.BAD_REQUEST,
    id(quota_exceeded): http.HTTPStatus.BAD_REQUEST,
    id(invalid_request_body): http.HTTPStatus.BAD_REQUEST,
    id(wrong_pod_profile): http.HTTPStatus.BAD_REQUEST,
    id(pod_not_found): http.HTTPStatus.NOT_FOUND,
    id(user_not_found): http.HTTPStatus.NOT_FOUND,
    id(username_required): http.HTTPStatus.BAD_REQUEST,
    id(user_not_allowed): http.HTTPStatus.FORBIDDEN,
}


def http_status_for(err: BaseException) -> int:
    """
    Map a known service-layer error sentinel to an HTTP status. Falls back to
    500 for anything we don't recognize as a user-facing error.
    """
    return USER_ERROR_HTTP_STATUS.get(id(err), http.HTTPStatus.INTERNAL_SERVER_ERROR)
