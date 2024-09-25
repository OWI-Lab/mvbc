import requests
import pytz
from datetime import datetime
from mvbc.config import Credentials
from mvbc.auth import BearerAuth
import os

rooturl = "https://api.meetnetvlaamsebanken.be"

def test_api_is_online():
    url = rooturl + "/V2/ping"
    response = requests.get(url).json()
    assert response['Customer'] == None

def test_expires_attribute():
    auth = BearerAuth("TOKEN", 'Tue, 25 Jan 2022 16:16:14 GMT')
    assert auth.expires == datetime(2022, 1, 25, 16, 16, 14, tzinfo=pytz.timezone('GMT'))


def test_authorization_header():
    url = rooturl + "/V2/ping"
    auth = BearerAuth("TOKEN", 'Tue, 25 Jan 2022 16:16:14 GMT')    
    response = requests.get(url, auth=auth)
    authorization = response.request.headers['authorization']
    assert authorization == 'Bearer TOKEN'
