import pytest


# Fixtures


@pytest.fixture
def options():
    return {
        "url": "https://demo.ckan.org/",
        "dataset": "frictionless",
        "apikey": "51912f57-a657-4caa-b2a7-0a1c16821f4b",
    }
