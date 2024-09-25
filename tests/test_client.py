import pytest
import time
import pytz
from datetime import datetime
from mvbc.client import Base
from mvbc.config import Credentials

def test_wrong_credentials():
    with pytest.raises(Exception) as exc_info:
        credentials = Credentials(username='a', password='1')
        Base(credentials=credentials)