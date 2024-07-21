"""
This module contains all the errors that can be raised by the application.
"""
import http


class Error(Exception):
    """
    Base class for other exceptions
    """
    code: http.HTTPStatus

    def __init__(self, *args, code=http.HTTPStatus.INTERNAL_SERVER_ERROR):
        self.code = code
        super().__init__(*args)

    @classmethod
    def from_exception(cls, e: Exception, code=http.HTTPStatus.INTERNAL_SERVER_ERROR):
        return Error(str(e), code=code)


access_denied = Error("access denied", code=http.HTTPStatus.FORBIDDEN)
db_connection_error = Error("db connection error")
duplicate_username = Error("duplicate username")
empty_username_or_password = Error("empty username or password")
header_malformed = Error("header malformed")
header_missing = Error("header missing")
invalid_request_body = Error("invalid request body")
invalid_token = Error("invalid token")
k8s_config_not_found = Error("Kubernetes config not found")
k8s_failed_to_create = Error("Kubernetes failed to create")
k8s_failed_to_delete = Error("Kubernetes failed to delete")
k8s_failed_to_get = Error("Kubernetes failed to get")
k8s_failed_to_list = Error("Kubernetes failed to list")
k8s_failed_to_update = Error("Kubernetes failed to update")
k8s_timeout = Error("Kubernetes timeout")
old_password_required = Error("old password required")
otp_code_required = Error("otp code required")
otp_code_wrong = Error("otp code wrong")
otp_password_required = Error("otp password required")
pod_not_found = Error("pod not found")
policy_not_found = Error("policy not found")
policy_cannot_be_deleted = Error("policy cannot be deleted")
policy_cannot_be_modified = Error("policy cannot be modified")
project_not_found = Error("project not found")
quota_exceeded = Error("quota exceeded")
template_invalid = Error("template invalid", code=http.HTTPStatus.BAD_REQUEST)
template_key_not_exists = Error("template key not exists")
template_key_not_used = Error("template key not used")
template_not_found = Error("template not found", code=http.HTTPStatus.NOT_FOUND)
unknown_error = Error("unknown error")
user_not_found = Error("user not found")
user_not_allowed = Error("user not allowed")
user_failed_to_parse = Error("user failed to parse")
user_exists = Error("user exists")
username_required = Error("username required")
username_illegal = Error("username illegal")
wrong_password = Error("wrong password")
wrong_pod_profile = Error("wrong pod profile")
wrong_query_filter = Error("wrong query filter")
wrong_template_profile = Error("wrong template profile")
wrong_user_profile = Error("wrong user profile")
