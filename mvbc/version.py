"""
This module exposes the current version of the package
so the version can be retreived directly within other code
files. The version assumes the semver notation (major.minor.patch-release.num).

Example:
    Import the version as constant, dict or tuple:

    >>> from mvbc.version import __version__, parse_version
    >>> parse_version(__version__)

Attributes:
    __version__ (str): Current version of mvbc package.

"""
import re
from typing import Optional, NamedTuple
from .__init__ import __version__

_REGEX = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:\-(?P<release>.*)\.(?P<num>\d+))?"


class Version(NamedTuple):
    """Convenience structure for interpreting the version information"""

    major: int
    minor: int
    patch: int
    release: Optional[str] = None
    num: Optional[int] = None


def parse_version(version: str) -> Version:
    """Converts the given version string to a named tuple per the semantic version guidelines"""
    match = re.search(_REGEX, version)
    if not match:
        raise ValueError(
            f"Version '{version}' does not comply with the semantic versioning naming scheme"
        )

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    release = match.group("release")

    num = None  # type: Optional[int]
    try:
        num = int(match.group("num"))
    except TypeError:
        pass

    return Version(
        major=major,
        minor=minor,
        patch=patch,
        release=release,
        num=num,
    )
