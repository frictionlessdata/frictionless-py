import pytest
from fastapi.testclient import TestClient

from frictionless.server import Client, Config, Server


@pytest.fixture
def client(tmpdir):
    client = Client(tmpdir)
    return client


@pytest.fixture(scope="session")
def api_client(tmpdir_factory):
    config = Config(folder=tmpdir_factory.mktemp("server"))
    server = Server.create(config)
    client = TestClient(server)
    return client
