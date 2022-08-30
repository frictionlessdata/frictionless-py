import os
import pytest
from fastapi.testclient import TestClient
from frictionless.server import server


@pytest.fixture
def api_client(tmpdir):
    server.config.basepath = os.path.join(tmpdir, "server")
    client = TestClient(server)
    return client
