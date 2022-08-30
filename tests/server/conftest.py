import pytest
from fastapi.testclient import TestClient
from frictionless.server import server


@pytest.fixture
def api_client():
    client = TestClient(server)
    return client
