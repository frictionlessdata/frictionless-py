# type: ignore
import json
import os
import pytest
from frictionless import portals, FrictionlessException
from .conftest import options, options_without_dp


# Read


@pytest.mark.vcr
def test_github_parser_read(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    control = portals.GithubControl()
    manager = portals.GithubManager(control)
    package = manager.read_package(user=user, repo=repo)
    assert json.loads(package.to_json()) == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv"
            },
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv"
            },
        ],
    }


@pytest.mark.vcr
def test_github_parser_read_without_apikey(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    control = portals.GithubControl()
    manager = portals.GithubManager(control)
    apikey = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    package = manager.read_package(user=user, repo=repo, apikey=apikey)
    assert json.loads(package.to_json()) == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv"
            },
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv"
            },
        ],
    }


@pytest.mark.vcr
def test_github_parser_read_without_datapackage(options_without_packages):
    user = options_without_packages.pop("user")
    repo = options_without_packages.pop("repo")
    control = portals.GithubControl()
    manager = portals.GithubManager(control)
    with pytest.raises(FrictionlessException) as excinfo:
        manager.read_package(user=user, repo=repo)
    error = excinfo.value.error
    assert error.message == "Package not found"


@pytest.mark.vcr
def test_github_parser_read_only_csv(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    control = portals.GithubControl()
    manager = portals.GithubManager(control)
    apikey = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    package = manager.read_package(user=user, repo=repo, apikey=apikey)
    assert json.loads(package.to_json()) == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv"
            },
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv"
            },
        ],
    }


@pytest.mark.vcr
def test_github_parser_read_other_file_types(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    control = portals.GithubControl(formats=["csv", "xlsx"])
    manager = portals.GithubManager(control)
    apikey = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    package = manager.read_package(user=user, repo=repo, apikey=apikey)
    assert json.loads(package.to_json()) == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv"
            },
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv"
            },
            {
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/student.xlsx"
            },
        ],
    }


# Write


@pytest.mark.vcr
def test_github_parser_write_package_file(options_write):
    repo = options_write.pop("repo")

    # Read - content to write to github
    content_file_path = "data/fixtures/portals/github/content.json"
    with open(content_file_path) as file:
        content = file.read()
    control = portals.GithubControl(repo=repo)
    manager = portals.GithubManager(control)
    response = manager.write_package(content=content)
    assert response.repository.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert repr(response.file_created["content"]) == f'ContentFile(path="package.json")'


# Search


@pytest.mark.vcr
def test_github_parser_read_catalog_with_search():
    control = portals.GithubControl(search="test user:fdtester")
    manager = portals.GithubManager(control=control)
    apikey = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    packages = manager.read_catalog(apikey=apikey)

    # Read
    output_file_path = "data/fixtures/portals/github/datapackage.json"
    with open(output_file_path) as file:
        packages[0].to_json() == json.loads(file.read())


@pytest.mark.vcr
def test_github_parser_read_catalog_without_search_text():
    control = portals.GithubControl()
    manager = portals.GithubManager(control=control)
    apikey = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    packages = manager.read_catalog(user="fdtester", apikey=apikey)

    # Read
    output_file_path = "data/fixtures/portals/github/datapackage.json"
    with open(output_file_path) as file:
        packages[0].to_json() == json.loads(file.read())
