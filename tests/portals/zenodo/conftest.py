import pytest


# Fixtures


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


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
def options_with_dp_with_remote_resources():
    return {
        "url": "https://zenodo.org/record/7097299",
        "record": "7097299",
    }
