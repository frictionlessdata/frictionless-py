import pytest


# Fixtures


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.fixture
def options():
    return {
        "url": "https://demo.ckan.org/",
        "dataset": "frictionless",
        "apikey": "51912f57-a657-4caa-b2a7-0a1c16821f4b",
    }


@pytest.fixture
def options_br():
    return {
        "url": "https://legado.dados.gov.br/",
        "dataset": "bolsa-familia-pagamentos",
    }


@pytest.fixture
def options_lh():
    return {
        "url": "http://localhost:5000/",
        "dataset": "dataset-example",
    }


@pytest.fixture
def options_datasets():
    return {
        "bolsa-familia-pagamentos": "https://legado.dados.gov.br/dataset/bolsa-familia-pagamentos",
    }


@pytest.fixture
def options_write():
    return {
        "url": "http://localhost:5000",
        "dataset": "test",
        "apikey": "",
    }
