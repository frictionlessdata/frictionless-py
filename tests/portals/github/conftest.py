import pytest


# Fixtures


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.fixture
def options_empty():
    return {
        "url": "https://github.com/fdtester/test-repo-empty",
        "user": "fdtester",
        "repo": "test-repo-empty",
    }


@pytest.fixture
def options_with_dp():
    return {
        "url": "https://github.com/fdtester/test-repo-with-datapackage-json",
        "user": "fdtester",
        "repo": "test-repo-with-datapackage-json",
    }


@pytest.fixture
def options_with_multiple_packages():
    return {
        "url": "https://github.com/fdtester/test-repo-with-multiple-packages",
        "user": "fdtester",
        "repo": "test-repo-with-multiple-packages",
    }


@pytest.fixture
def options_without_dp():
    return {
        "url": "https://github.com/fdtester/test-repo-without-datapackage",
        "user": "fdtester",
        "repo": "test-repo-without-datapackage",
        "output": {
            "name": "test-repo-without-datapackage",
            "resources": [
                {
                    "name": "capitals",
                    "type": "table",
                    "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv",
                    "scheme": "https",
                    "format": "csv",
                    "mediatype": "text/csv",
                },
                {
                    "name": "countries",
                    "type": "table",
                    "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv",
                    "scheme": "https",
                    "format": "csv",
                    "mediatype": "text/csv",
                },
            ],
        },
        "output_with_xls": {
            "name": "test-repo-without-datapackage",
            "resources": [
                {
                    "name": "capitals",
                    "type": "table",
                    "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv",
                    "scheme": "https",
                    "format": "csv",
                    "mediatype": "text/csv",
                },
                {
                    "name": "countries",
                    "type": "table",
                    "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv",
                    "scheme": "https",
                    "format": "csv",
                    "mediatype": "text/csv",
                },
                {
                    "name": "student",
                    "type": "table",
                    "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/student.xlsx",
                    "scheme": "https",
                    "format": "xlsx",
                    "mediatype": "application/vnd.ms-excel",
                },
            ],
        },
    }


@pytest.fixture
def options_write():
    return {
        "url": "https://github.com/fdtester/test-repo-write",
        "user": "fdtester",
        "repo": "test-repo-write",
    }


@pytest.fixture
def options_write_test_params():
    return {
        "url": "https://github.com/fdtester/test-repo-write-with-params",
        "user": "fdtester",
        "repo": "test-repo-write-with-params",
    }


@pytest.fixture
def options_publish_test_params():
    return {
        "url": "https://github.com/fdtester/test-repo-publish",
        "user": "fdtester",
        "repo": "test-repo-publish",
    }
