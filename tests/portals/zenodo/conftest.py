import os
import pytest


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
        "url": "https://zenodo.org/record/7078760",
        "record": "7078760",
    }


@pytest.fixture
def options_without_dp():
    return {
        "url": "https://zenodo.org/record/7078768",
        "record": "7078768",
    }


@pytest.fixture
def options_with_dp_multiple_files_with_dp():
    return {
        "url": "https://zenodo.org/record/7078710",
        "record": "7078710",
    }


@pytest.fixture
def options_with_dp_multiple_files_without_dp():
    return {
        "url": "https://zenodo.org/record/7078725",
        "record": "7078725",
    }


@pytest.fixture
def options_with_dp_multiple_files_with_zipped_files():
    return {
        "url": "https://zenodo.org/record/7077932",
        "record": "7077932",
    }


@pytest.fixture
def options_without_dp_with_zipped_files():
    return {
        "url": "https://zenodo.org/record/7247979",
        "record": "7077932",
    }


@pytest.fixture
def options_with_dp_with_remote_resources():
    return {
        "url": "https://zenodo.org/record/7097299",
        "record": "7097299",
    }


@pytest.fixture
def options_with_zipped_resource_file():
    return {
        "url": "https://zenodo.org/record/7248153",
        "record": "7248153",
    }


@pytest.fixture
def sandbox_api():
    sandbox_api = os.environ.get("ZENODO_SANDBOX_ACCESS_TOKEN")
    return sandbox_api
