import re
import uuid

_rfc1123_pattern = re.compile("^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$")


def is_valid_rfc1123(s: str):
    """
    Check if a string meets the requirements defined in RFC1123.

    :param s: The string to check.
    :return: True if it's valid, False otherwise.
    """

    return bool(_rfc1123_pattern.match(s))


print(is_valid_rfc1123("www.google.com"))
print(is_valid_rfc1123("TEST1-basic-auth"))
print(is_valid_rfc1123("test"))
print(is_valid_rfc1123("test-"))
print(is_valid_rfc1123("test-1"))
print(is_valid_rfc1123("TEST1."))
print(is_valid_rfc1123(f"{uuid.uuid4()}-basic-auth"))
