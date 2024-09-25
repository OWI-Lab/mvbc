import logging
import pytest
import sys
import os
import json
from distutils import dir_util
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock
from mvbc.config import Credentials
from mvbc.objects import Data

logger = logging.getLogger(__name__)

VERSION = "0.2.2"

# Add custom options to pytest. Here we define the addition of an 'url' argument
# so you could run `pytest --url <url>` to specify an external url to check real time
# api calls for instance.
# Also it can skip tests that need this fixture but the argument was not passed to the
# pytest command.
def pytest_addoption(parser):
    """Adds option to pytest command

    '--url <url>' to specify the url of the api during CI
    """
    parser.addoption("--url", action="store")


@pytest.fixture
def url(request):
    """Returns URL if defined or skips test"""
    url_value = request.config.option.url
    if url_value is None:
        pytest.skip()
    return url_value


# Isolated data folder to tests things that require files.
@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.

    Usage:
    # If test module is called: test_files.py
    # Create folder tests/test_files (same name as test module file)
    # Put <filename> in that folder
    # Create tests like:
    >>> def test_file_stuff(datadir):
    >>>     path = datadir.join("<filename>")
    >>>     # Open file using `path`
    >>>     # Test something with file contents
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir

@pytest.fixture
def sample_dict_data():
    return {
        "Values": [
            {
                "ID": "WS1",
                "Values": [
                    {"Timestamp": "2023-01-01T00:00:00Z", "Value": 10},
                    {"Timestamp": "2023-01-01T01:00:00Z", "Value": 12},
                ],
            },
            {
                "ID": "WS2",
                "Values": [],  # No data available
            },
        ]
    }

@pytest.fixture
def sample_df_weatherstations():
    data = {
        "Name": ["Thorntonbank - Station A", "Wandelaar - Station B", "Westhinder - Station C"],
        "Parameter": ["P1", "P2", "P3"],  # This should not be empty
        "ID": ["WS1", "WS2", "WS3"],
        "ParameterName": ["Temp", "Humidity", "WindSpeed"],
        "Description": ["Thorntonbank Station A", "Wandelaar Station B", "Westhinder Station C"],
        "ParameterUnit": ["C", "%", "m/s"],
        "PositionWKT": ["POINT (52.0 4.0)", "POINT (53.0 5.0)", "POINT (54.0 6.0)"],
    }
    return pd.DataFrame(data, index=["WS1", "WS2", "WS3"])