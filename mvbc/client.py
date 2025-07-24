"""
Meetnet Vlaamse Banken Client

Module to fetch the Data of the Flemish Banks Monitoring Network via API request.

Consult the `API Documentation <https://api.meetnetvlaamsebanken.be/V2-help>`_
for more information on the different endpoints, request and response models.
"""
from typing import Optional, Any
from datetime import datetime
import requests
import pytz


from .auth import BearerAuth
from .config import Credentials


class Base:
    """Base Class

    Implements authentication and API systems verification (ping)

    Args:
        credentials: (Optional), by default the credentials are
            loaded from :code:`.env` file or env variables.

    Attributes:
        auth: The :class:`BearerAuth` object which can be passed to a request directly
        url: The base URL of the API (`<https://api.meetnetvlaamsebanken.be>`_)

    """

    def __init__(self, credentials: Optional[Credentials] = None):

        if credentials is None:
            credentials = Credentials()  # type: ignore

        self.user: str = credentials.username
        self.password: str = credentials.password
        self.url: str = "https://api.meetnetvlaamsebanken.be"
        self.auth: Optional[BearerAuth] = None
        self.login()

    def login(self) -> Optional[BearerAuth]:
        """
        Get the access token.

        Returns:
            :class:`BearerAuth` object with the correct access token,
            which can be used for authentication
        """
        url = self.url + "/Token"
        now = datetime.now(pytz.timezone("Europe/Brussels")).astimezone(pytz.UTC)
        if self.auth and now < self.auth.expires:
            return

        response = requests.post(
            url,
            {
                "username": self.user,
                "password": self.password,
                "grant_type": "password",
            },
        )
        if response.status_code != 200:
            raise Exception(
                "This username and password are not valid!" "Please register first."
            )
        data = response.json()
        token = data["access_token"]
        expires = data[".expires"]
        self.auth = BearerAuth(token, expires)

    def ping(self, login: bool = True) -> Any:
        """Ping request

        The ping request can be used to check if this system is up and running and/or
        if it is reachable through your companys firewalls.
        You don't need to be logged in to call this request.
        Add :code:`login=False` as parameter in that case.

        A second usage for this command is to check the login system.
        If you are successfully logged in, the response will contain a Customer Property,
        otherwise this property remains null.

        Args:
            login (bool, optional): Perform automatic login using the passed credentials.
                Defaults to True.

        Returns:
            Response string in JSON format
        """
        url = self.url + "/V2/ping"
        if not login:
            return requests.get(url).json()

        self.login()
        return requests.get(url, auth=self.auth).json()
