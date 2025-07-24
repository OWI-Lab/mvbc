"""
Settings configuration

The Meetnet Vlaamse Banken API requires credentials for the API calls.
Following the 12-factor app methodology, configuration should be stored in the
environment. Therefore a config module was added to load these values from
a `.env` file or environmental variables.

Examples:
    >>> from mvbc.config import Credentials
    >>> creds = Credentials(username="user", password="example")
    >>> print(creds.username)
    user

    Or from `.env` or environmental variables with the latter having priority

    >>> s = Credentials()
"""
import os
from typing import Optional
from dotenv import load_dotenv


class ValidationError(Exception):
    """Custom validation error class"""
    pass


class Credentials:
    """Configuration class model

    The model initialiser will attempt to determine the values of the fields.

    Values not passed as keyword arguments when initializing this class will be looked up
    by reading from the environment. Check the env variables MVBC_USERNAME and MVBC_PASSWORD.
    The priority for lookup is (1) keyword arguments (2) environment variables and (3) `.env` file.

    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        env_file: Optional[str] = None,
        env_file_encoding: str = "utf-8",
    ):
        if env_file is not None:
            load_dotenv(env_file, env_file_encoding)  # doesn't override env vars
        env_username = os.getenv("MVBC_USERNAME")
        env_password = os.getenv("MVBC_PASSWORD")

        # Override with direct parameters (highest priority)
        final_username = username if username is not None else env_username
        final_password = password if password is not None else env_password

        # Validate required fields
        errors = []
        if final_username is None:
            raise ValidationError("MVBC_USERNAME is not set")
        if final_password is None:
            raise ValidationError("MVBC_PASSWORD is not set")

        # Set the attributes
        self.username: str = final_username
        self.password: str = final_password

    def __eq__(self, other) -> bool:
        """Allow comparison with dictionaries."""
        if isinstance(other, dict):
            return other == {"username": self.username, "password": self.password}
        elif isinstance(other, Credentials):
            return self.username == other.username and self.password == other.password
        return False
