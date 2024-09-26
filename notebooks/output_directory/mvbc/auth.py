"""
Bearer authentication setup
"""
from datetime import datetime
import requests
import pytz


class BearerAuth(requests.auth.AuthBase):
    """Custom authentication class for Meetnet Vlaamse Banken API.

    When an authentication handler is attached to a request, it is called during request setup
    and will present the required authorization header containing the 'Bearer <TOKEN>' directive.

    Note:
        Check the `authentication section
        <https://docs.python-requests.org/en/latest/
        user/authentication/#new-forms-of-authentication>`_ of
        the `requests` documentation for more info.

    Args:
        token: Access token used to authenticate with the API.
        expires: A :class:`datetime` with the expiry date and time of the
            authentication token.

    Attributes:
        token: Access token used to authenticate with the API.
        expires: A :class:`datetime` with the expiry date and time of the
            authentication token.
    """

    def __init__(self, token: str, expires: str):
        self.token = token
        tz = pytz.timezone("GMT")
        expires_dt = datetime.strptime(expires, "%a, %d %b %Y %H:%M:%S %Z")
        self.expires = tz.localize(expires_dt)

    # NOTE: No docstring required for special methods, but always good to have
    # They can be enabled by changing the following
    # setting in Sphinx's conf.py:
    #
    #       napoleon_include_special_with_doc = True
    def __call__(self, r: requests.request) -> requests.request:
        """Add authorization header to request.

        The API defines that after login all the subsequent requests must have
        the resulting Bearer Acces Token in the HTTP headers:
        `Authorization: Bearer 1234567890ABCDEF......`

        Args:
            r: The original request.

        Returns:
            Requests object where `authorization` header includes the bearer token.
        """
        r.headers["authorization"] = "Bearer " + self.token
        return r
