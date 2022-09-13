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
def options_with_duplicate_files():
    return {
        "url": "https://github.com/fdtester/test-repo-files-in-multiple-folders-duplicate-files",
        "user": "fdtester",
        "repo": "test-repo-files-in-multiple-folders-duplicate_files",
    }


@pytest.fixture
def options_with_multiple_folders():
    return {
        "url": "https://github.com/fdtester/test-repo-files-in-multiple-folders",
        "user": "fdtester",
        "repo": "test-repo-files-in-multiple-folders",
    }


@pytest.fixture
def options_with_dp_yaml():
    return {
        "url": "https://github.com/fdtester/test-repo-with-datapackage-yaml",
        "user": "fdtester",
        "repo": "test-repo-with-datapackage-yaml",
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


# Write/Publish


@pytest.fixture
def options_write():
    return {
        "url": "https://github.com/fdtester/test-write",
        "user": "fdtester",
        "repo": "test-write",
    }


@pytest.fixture
def options_write_test_params():
    return {
        "url": "https://github.com/fdtester/test-write-with-params",
        "user": "fdtester",
        "repo": "test-write-with-params",
    }


@pytest.fixture
def options_publish_test_params():
    return {
        "url": "https://github.com/fdtester/test-publish",
        "user": "fdtester",
        "repo": "test-publish",
    }


# Catalog


@pytest.fixture
def options_user():
    return {"url": "https://github.com/fdtester/", "user": "fdtester"}
