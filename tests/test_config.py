import pytest
from mvbc.config import Credentials, ValidationError


def test_config_from_class_init():
    s = Credentials(username="a", password="1")
    assert s == {'username': 'a', 'password': '1'}

def test_config_from_dotenv(datadir, monkeypatch):    
    monkeypatch.delenv("MEETNET_USERNAME", raising=False)
    monkeypatch.delenv("MEETNET_PASSWORD", raising=False)
    path = datadir.join("dotenv")
    s = Credentials(env_file=path, env_file_encoding='utf-8')
    assert s == {'username': 'ab', 'password': '12'}

def test_config_from_envvar(monkeypatch):
    monkeypatch.delenv("MEETNET_USERNAME", raising=False)
    monkeypatch.delenv("MEETNET_PASSWORD", raising=False)
    monkeypatch.setenv("MEETNET_USERNAME", "abc")
    monkeypatch.setenv("MEETNET_PASSWORD", "123")
    # Load from env vars
    s = Credentials()
    assert s == {'username': 'abc', 'password': '123'}

def test_config_priority(datadir, monkeypatch):
    """class-params > env-vars > dotenv"""
    # Load from dotenv file
    path = datadir.join("dotenv")
    s = Credentials(env_file=path,env_file_encoding='utf-8')
    assert s == {'username': 'ab', 'password': '12'}

    # Define Environmental variables. Still loads from dotenv file since it 
    # ovverides
    monkeypatch.setenv("MEETNET_USERNAME", "abc")
    monkeypatch.setenv("MEETNET_PASSWORD", "123")
    s = Credentials(env_file=path, env_file_encoding='utf-8')
    assert s == {'username': 'ab', 'password': '12'}

    # Pass config parameters via class
    s = Credentials(username="a", password="1", env_file=path, env_file_encoding='utf-8')
    assert s == {'username': 'a', 'password': '1'}
    
    # Load from env vars
    monkeypatch.setenv("MEETNET_USERNAME", "abc")
    monkeypatch.setenv("MEETNET_PASSWORD", "123")
    s = Credentials()
    assert s == {'username': 'abc', 'password': '123'}

def test_config_missing_password(monkeypatch):
    monkeypatch.delenv("MEETNET_USERNAME", raising=False)
    monkeypatch.delenv("MEETNET_PASSWORD", raising=False)
    with pytest.raises(ValidationError, match='MEETNET_PASSWORD is not set'):
        Credentials(username='a', env_file=None)
