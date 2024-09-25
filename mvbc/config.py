"""
Settings configuration

The Meetnet Vlaamse Banken API requires credentials for the API calls.
Following the 12-factor app methodology, configuration should be stored in the
environment. Therefore a config module was added to load these values from
a `.env` file or environmental variables.
See `pydantic settings management <https://pydantic-docs.helpmanual.io/usage/settings/>`_ for
more information.

Examples:
    >>> from mvbc.config import Credentials
    >>> creds = Credentials(username="user", password="example")
    >>> print(creds.username)
    user

    Or from `.env` or environmental variables with the latter having priority

    >>> s = Credentials()
"""
from pydantic import BaseSettings, Field


class Credentials(BaseSettings):
    """Configuration class model

    The model initialiser will attempt to determine the values of the fields.

    Values not passed as keyword arguments when initializing this class will be looked up
    by reading from the environment. Check the `env` property in the JSON docs for the expected
    name. The priority for lookup is (1) environment variables and (2) `.env` file.

    """

    username: str = Field(
        ..., env="MVBC_USERNAME", description="The user used to authenticate. "
    )
    password: str = Field(
        ..., env="MVBC_PASSWORD", description="The password used for authentication."
    )

    class Config:
        # pylint: disable=missing-class-docstring, too-few-public-methods
        env_file = ".env"
        env_file_encoding = "utf-8"
