import pytest
from mvbc.config import Credentials
from pydantic.error_wrappers import ValidationError

def test_config_from_class_init():
    s = Credentials(username="a", password="1")
    assert s == {'username': 'a', 'password': '1'}

def test_config_from_dotenv(datadir, monkeypatch):    
    monkeypatch.delenv("MVBC_USERNAME", raising=False)
    monkeypatch.delenv("MVBC_PASSWORD", raising=False)
    path = datadir.join("dotenv")
    s = Credentials(_env_file=path, _env_file_encoding='utf-8')
    assert s == {'username': 'ab', 'password': '12'}

def test_config_from_envvar(monkeypatch):
    monkeypatch.delenv("MVBC_USERNAME", raising=False)
    monkeypatch.delenv("MVBC_PASSWORD", raising=False)
    monkeypatch.setenv("MVBC_USERNAME", "abc")
    monkeypatch.setenv("MVBC_PASSWORD", "123")
    s = Credentials()
    assert s == {'username': 'abc', 'password': '123'}

def test_config_priority(datadir, monkeypatch):
    """class-params > env-vars > dotenv"""
    monkeypatch.delenv("MVBC_USERNAME", raising=False)
    monkeypatch.delenv("MVBC_PASSWORD", raising=False)
    # Load from dotenv file
    path = datadir.join("dotenv")
    s = Credentials(_env_file=path, _env_file_encoding='utf-8')
    assert s == {'username': 'ab', 'password': '12'}

    # Define Environmental variables
    monkeypatch.setenv("MVBC_USERNAME", "abc")
    monkeypatch.setenv("MVBC_PASSWORD", "123")
    s = Credentials(_env_file=path, _env_file_encoding='utf-8')
    assert s == {'username': 'abc', 'password': '123'}

    # Pass config parameters via class
    s = Credentials(username="a", password="1", _env_file=path, _env_file_encoding='utf-8')
    assert s == {'username': 'a', 'password': '1'}

def test_config_missing_password(monkeypatch):
    monkeypatch.delenv("MVBC_USERNAME", raising=False)
    monkeypatch.delenv("MVBC_PASSWORD", raising=False)
    with pytest.raises(ValidationError) as exc_info:
        Credentials(username="a", _env_file=None) # Override env file
    password_error = {'loc': ('password',), 'msg': 'field required', 'type': 'value_error.missing'}   
    assert exc_info.value.errors()[0] == password_error
    
