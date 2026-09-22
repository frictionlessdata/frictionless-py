import os

import pytest

from frictionless import platform

# Fixtures


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "filter_query_parameters": ["access_token"],
    }


@pytest.fixture
def options_with_dp():
    return {
        "url": "https://zenodo.org/records/7078760",
        "record": "7078760",
    }


@pytest.fixture
def options_without_dp():
    return {
        "url": "https://zenodo.org/records/7078768",
        "record": "7078768",
    }


@pytest.fixture
def options_with_dp_multiple_files_with_dp():
    return {
        "url": "https://zenodo.org/records/7078710",
        "record": "7078710",
    }


@pytest.fixture
def options_with_dp_multiple_files_without_dp():
    return {
        "url": "https://zenodo.org/records/7078725",
        "record": "7078725",
    }


@pytest.fixture
def options_with_dp_multiple_files_with_zipped_files():
    return {
        "url": "https://zenodo.org/records/7077932",
        "record": "7077932",
    }


@pytest.fixture
def options_without_dp_with_zipped_files():
    return {
        "url": "https://zenodo.org/records/7247979",
        "record": "7077932",
    }


@pytest.fixture
def options_with_dp_with_remote_resources():
    return {
        "url": "https://zenodo.org/records/7097299",
        "record": "7097299",
    }


@pytest.fixture
def options_with_zipped_resource_file():
    return {
        "url": "https://zenodo.org/records/7248153",
        "record": "7248153",
    }


@pytest.fixture
def sandbox_control(tmp_path):
    sandbox_token = os.environ.get("ZENODO_SANDBOX_ACCESS_TOKEN")
    if sandbox_token is None:
        pytest.skip("ZENODO_SANDBOX_ACCESS_TOKEN environment variable not set")
    return {
        "apikey": sandbox_token,
        "base_url": "https://sandbox.zenodo.org/api/",
        "tmp_path": tmp_path,
    }


@pytest.fixture(scope="session")
def shared_deposition_id():
    # unfortunately we cannot use the `sandbox_control` fixture here,
    # since it is not session scoped (and cannot be due to `tmp_path`)
    token = os.environ.get("ZENODO_SANDBOX_ACCESS_TOKEN")
    if token is None:
        pytest.skip("ZENODO_SANDBOX_ACCESS_TOKEN environment variable not set")

    return platform.pyzenodo3_upload.create(
        token=token, base_url="https://sandbox.zenodo.org/api/"
    )
