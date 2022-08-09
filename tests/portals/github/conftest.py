import pytest


# Fixtures


@pytest.fixture
def options():
    return {
        "url": "https://github.com/fdtester/test-repo-with-datapackage-json",
        "user": "fdtester",
        "repo": "test-repo-with-datapackage-json",
    }


@pytest.fixture
def options_without_dp():
    return {
        "url": "https://github.com/fdtester/test-repo-without-datapackage",
        "user": "fdtester",
        "repo": "test-repo-without-datapackage",
    }


@pytest.fixture
def options_without_packages():
    return {
        "url": "https://github.com/fdtester/test-repo-empty",
        "user": "fdtester",
        "repo": "test-repo-empty",
    }


@pytest.fixture
def options_write():
    return {
        "url": "https://github.com/fdtester/test-repo-write",
        "user": "fdtester",
        "repo": "test-repo-write",
    }
