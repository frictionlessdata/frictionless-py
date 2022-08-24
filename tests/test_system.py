import pytest
import requests
from frictionless import Resource, system, schemes


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


@pytest.mark.vcr
def test_system_use_context_http_session():
    session = requests.Session()
    with system.use_context(http_session=session):
        assert system.http_session is session
        with Resource(BASEURL % "data/table.csv") as resource:
            control = resource.dialect.get_control("remote")
            assert isinstance(control, schemes.RemoteControl)
            assert resource.header == ["id", "name"]
    assert system.http_session is not session
