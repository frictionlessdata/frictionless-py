# type: ignore
import json
import pytest
from frictionless import portals, Catalog, Package, FrictionlessException


# Read


@pytest.mark.vcr
def test_github_manager_read(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    package = Package(url)
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_read_without_apikey(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    package = Package.from_github(url, control=portals.GithubControl(apikey=None))
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_read_repo_with_datapackage(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert json.loads(package.to_json()) == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_read_no_datapackage_found(options_empty):
    url = options_empty.pop("url")
    control = portals.GithubControl()
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github(url, control=control)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_manager_read_only_csv_default(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    control = portals.GithubControl()
    package = Package.from_github(url, control=control)
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_read_other_file_types(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output_with_xls")
    control = portals.GithubControl(formats=["csv", "xlsx"])
    package = Package.from_github(url, control=control)
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_read_with_url_and_control(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.GithubControl(formats=["xlsx"])
    package = Package.from_github(url, control=control)
    assert json.loads(package.to_json()) == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "name": "student",
                "type": "table",
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/student.xlsx",
                "scheme": "https",
                "format": "xlsx",
                "mediatype": "application/vnd.ms-excel",
            },
        ],
    }


@pytest.mark.vcr
def test_github_manager_read_with_wrongurl():
    url = "test"
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github(url, control=portals.GithubControl())
    error = excinfo.value.error
    assert error.message == "Not supported Github source: test"


@pytest.mark.vcr
def test_github_manager_read_without_url_with_controls(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    output = options_without_dp.pop("output")
    package = Package(control=portals.GithubControl(user=user, repo=repo))
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_alias(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    package = Package.from_github(url)
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_alias_read_multiple_file_types(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output_with_xls")
    control = portals.GithubControl(formats=["csv", "xlsx"])
    package = Package.from_github(url, control=control)
    assert json.loads(package.to_json()) == output


@pytest.mark.vcr
def test_github_manager_alias_without_url_with_controls(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    output = options_without_dp.pop("output")
    package = Package.from_github(control=portals.GithubControl(user=user, repo=repo))
    assert json.loads(package.to_json()) == output


# Write


@pytest.mark.vcr
def test_github_manager_write_package_file(options_write):
    target_url = options_write.pop("url")
    repo = options_write.pop("repo")
    package = Package("data/datapackage.json")
    response = package.to_github(target=target_url)
    assert response.repository.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.file_created["content"]) == f'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
def test_github_manager_write_package_file_with_bad_credentials(options_write):
    target_url = options_write.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        package = Package("data/datapackage.json")
        package.to_github(target=target_url, control=portals.GithubControl(apikey="test"))
    error = excinfo.value.error
    assert "Bad credentials" in error.message
    assert "Github API error:BadCredentialsException" in error.message


@pytest.mark.vcr
def test_github_manager_write_package_file_with_no_credentials(options_write):
    target_url = options_write.pop("url")
    with pytest.raises(AssertionError) as excinfo:
        package = Package("data/datapackage.json")
        package.to_github(target=target_url, control=portals.GithubControl(apikey=None))
    assert "AssertionError" in str(excinfo)


@pytest.mark.vcr
def test_github_manager_write_package_file_with_no_params():
    with pytest.raises(FrictionlessException) as excinfo:
        package = Package("data/datapackage.json")
        package.to_github()
    error = excinfo.value.error
    assert error.message == "Not supported target: None"


@pytest.mark.vcr
def test_github_manager_write_package_file_with_additional_params(
    options_write_test_params,
):
    target_url = options_write_test_params.pop("url")
    repo = options_write_test_params.pop("repo")
    package = Package("data/datapackage.json")
    response = package.to_github(
        target=target_url,
        control=portals.GithubControl(
            filename="package.json", email="info@okfn.org", name="FD"
        ),
    )
    assert response.repository.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert repr(response.file_created["content"]) == f'ContentFile(path="package.json")'


@pytest.mark.vcr
def test_github_manager_write_package_file_without_target_url():
    package = Package("data/datapackage.json")
    response = package.to_github(
        control=portals.GithubControl(repo="test-repo-write-without-url")
    )
    assert (
        response.repository.url
        == f"https://api.github.com/repos/fdtester/test-repo-write-without-url"
    )
    assert (
        repr(response.file_created["content"]) == f'ContentFile(path="datapackage.json")'
    )


# Publish


@pytest.mark.vcr
def test_github_manager_publish_to_github(options_publish_test_params):
    target_url = options_publish_test_params.pop("url")
    repo = options_publish_test_params.pop("repo")
    package = Package("data/datapackage.json")
    response = package.to_github(target=target_url)
    assert response.repository.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.file_created["content"]) == f'ContentFile(path="datapackage.json")'
    )


# Search


@pytest.mark.vcr
def test_github_manager_catalog_from_repo_with_single_package(options_write):
    repo_url = options_write.pop("url")
    catalog = Catalog(repo_url)

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert json.loads(catalog.packages[0].to_json()) == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_from_repo_with_multiple_packages(
    options_with_multiple_packages,
):
    repo_url = options_with_multiple_packages.pop("url")
    catalog = Catalog(repo_url)
    assert len(catalog.packages) == 2
    assert catalog.packages[0].name == "test-tabulator-json"
    assert catalog.packages[1].name == "test-tabulator-yaml"


@pytest.mark.vcr
def test_github_manager_catalog_with_search_param_only_containing_userqualifier():
    catalog = Catalog(
        control=portals.GithubControl(search="test-repo-write user:fdtester"),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert json.loads(catalog.packages[0].to_json()) == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_with_search_having_userqualifier_and_user_param():
    catalog = Catalog(
        control=portals.GithubControl(search="test-repo-write", user="fdtester"),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert json.loads(catalog.packages[0].to_json()) == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_with_search_text_and_without_user_or_userqualifier():
    catalog = Catalog(
        control=portals.GithubControl(search="frictionlessdata", per_page=2, page=1),
    )
    assert catalog.packages[0].name == "schemas"
    assert catalog.packages[1].name == "fellows"


@pytest.mark.vcr
def test_github_manager_catalog_with_user_param_only():
    catalog = Catalog(
        control=portals.GithubControl(user="fdtester"),
    )
    assert len(catalog.packages) == 7

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert json.loads(catalog.packages[3].to_json()) == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_with_repo_param_only():
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            control=portals.GithubControl(repo="test-repo-without-datapackage"),
        )
    error = excinfo.value.error
    assert "invalid" in error.message
    assert "Github API errorGithubException" in error.message


@pytest.mark.vcr
def test_github_manager_catalog_without_search_user_repo_params():
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            control=portals.GithubControl(),
        )
    error = excinfo.value.error
    assert error.message == "Repo or user or search text is required"


@pytest.mark.vcr
def test_github_manager_catalog_with_full_path_repo_only(options_without_dp):
    output = options_without_dp.pop("output")
    catalog = Catalog(
        control=portals.GithubControl(repo="fdtester/test-repo-without-datapackage"),
    )
    assert json.loads(catalog.packages[0].to_json()) == output


@pytest.mark.vcr
def test_github_manager_catalog_custom_per_page():
    catalog = Catalog(
        control=portals.GithubControl(user="frictionlessdata", per_page=2, page=1),
    )
    assert len(catalog.packages) == 2


@pytest.mark.vcr
def test_github_manager_catalog_page():
    catalog = Catalog(
        control=portals.GithubControl(user="fdtester", per_page=2, page=3),
    )
    assert catalog.packages[0].resources[0].name == "capitals"


@pytest.mark.vcr
def test_github_manager_catalog_with_searchtext_and_empty_packages():
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            control=portals.GithubControl(search="user:fdtester test-repo-empty"),
        )
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers(options_without_dp):
    output = options_without_dp.pop("output")
    catalog = Catalog(
        control=portals.GithubControl(
            search="Frictionlessdata in:readme", user="fdtester"
        ),
    )
    assert json.loads(catalog.packages[0].to_json()) == output


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_qualifier(options_without_dp):
    output = options_without_dp.pop("output")
    catalog = Catalog(
        control=portals.GithubControl(search="sort:updated", user="fdtester"),
    )
    assert json.loads(catalog.packages[3].to_json()) == output


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_param(options_without_dp):
    output = options_without_dp.pop("output")
    catalog = Catalog(
        control=portals.GithubControl(sort="updated", user="fdtester"),
    )
    assert json.loads(catalog.packages[0].to_json()) == output


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_by_updated_in_desc_order(
    options_without_dp,
):
    output = options_without_dp.pop("output")
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated", user="fdtester", order="desc"
        ),
    )
    assert json.loads(catalog.packages[3].to_json()) == output
