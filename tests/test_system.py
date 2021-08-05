import pytest
import requests
from frictionless import Resource, system


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


@pytest.mark.vcr
def test_system_use_http_session():
    session = requests.Session()
    with system.use_http_session(session):
        assert system.get_http_session() is session
        with Resource(BASEURL % "data/table.csv") as resource:
            assert resource.control.http_session is session
            assert resource.header == ["id", "name"]
    assert system.get_http_session() is not session
