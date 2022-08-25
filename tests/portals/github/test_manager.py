# type: ignore
import json
import pytest
from frictionless import portals, platform, Catalog, Package, FrictionlessException


# Read


@pytest.mark.vcr
def test_github_manager_read(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    package = Package(url)
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_read_without_apikey(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    package = Package.from_github(url, control=portals.GithubControl(apikey=None))
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_read_repo_with_datapackage(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert package.to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_read_no_datapackage_found(options_empty):
    url = options_empty.pop("url")
    control = portals.GithubControl()
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github(url, control=control)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_manager_read_default(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    control = portals.GithubControl()
    package = Package.from_github(url, control=control)
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_read_other_file_types(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output_csv_only")
    control = portals.GithubControl(formats=["csv"])
    package = Package.from_github(url, control=control)
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_read_with_url_and_control(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.GithubControl(formats=["xlsx"])
    package = Package.from_github(url, control=control)
    assert package.to_descriptor() == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "name": "student",
                "type": "table",
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/student.xlsx",
                "scheme": "https",
                "format": "xlsx",
                "mediatype": "application/vnd.ms-excel",
            }
        ],
    }


@pytest.mark.vcr
def test_github_manager_read_with_wrongurl():
    url = "test"
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github(url, control=portals.GithubControl())
    error = excinfo.value.error
    assert error.message == "Not supported Github source 'test' or control"


@pytest.mark.vcr
def test_github_manager_read_without_url_with_controls(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    output = options_without_dp.pop("output")
    package = Package(control=portals.GithubControl(user=user, repo=repo))
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_alias(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output")
    package = Package.from_github(url)
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_alias_read_custom_file_types(options_without_dp):
    url = options_without_dp.pop("url")
    output = options_without_dp.pop("output_csv_only")
    control = portals.GithubControl(formats=["csv"])
    package = Package.from_github(url, control=control)
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_alias_without_url_with_controls(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    output = options_without_dp.pop("output")
    package = Package.from_github(control=portals.GithubControl(user=user, repo=repo))
    assert package.to_descriptor() == output


def test_github_manager_read_without_repo_user():
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github(control=portals.GithubControl())
    error = excinfo.value.error
    assert error.message == "Repo and user is required"


def test_github_manager_read_without_url_and_control_params():
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github()
    error = excinfo.value.error
    assert error.message == "Not supported Github source 'None' or control"


@pytest.mark.vcr
def test_github_manager_read_yaml(options_with_dp_yaml):
    url = options_with_dp_yaml.pop("url")
    output = options_with_dp_yaml.pop("output")
    package = Package(url)
    assert package.to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_read_resource_with_duplicate_packages(
    options_with_duplicate_files,
):
    url = options_with_duplicate_files.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_github(url)
    error = excinfo.value.error
    assert (
        error.message
        == 'The data package has an error: resource "table-reverse" already exists'
    )


@pytest.mark.vcr
def test_github_manager_read_resources(options_with_dp):
    url = options_with_dp.pop("url")
    packages = Package.from_github(url)
    assert len(packages.resources) == 2
    assert packages.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_github_manager_read_package_with_files_in_multiple_folders(
    options_with_multiple_folders,
):
    url = options_with_multiple_folders.pop("url")
    packages = Package.from_github(url)
    assert len(packages.resources) == 3
    assert packages.resources[0].name == "first-resource"
    assert packages.resources[1].name == "number-two"
    assert packages.resources[2].name == "countries"


@pytest.mark.vcr
def test_github_manager_read_resources_without_dp(options_without_dp):
    url = options_without_dp.pop("url")
    packages = Package.from_github(url)
    assert len(packages.resources) == 3
    assert packages.resources[0].name == "capitals"
    assert (
        packages.resources[0].path
        == "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv"
    )


# Write


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file_with_descriptor_empty_resources():
    repo = "test-write-package-with-descriptor-without-resources"
    descriptor = {
        "name": "test-tabulator",
        "resources": [
            {
                "name": "first-resource",
                "path": "data/table.xls",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "number"},
                        {"name": "name", "type": "string"},
                    ]
                },
            }
        ],
    }
    package = Package(descriptor)
    response = package.to_github(
        control=portals.GithubControl(user="fdtester", repo=repo)
    )
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file_with_descriptor():
    repo = "test-write-package-with-descriptor"
    descriptor = {"name": "test-tabulator", "resources": []}
    package = Package(descriptor)
    response = package.to_github(
        control=portals.GithubControl(user="fdtester", repo=repo)
    )
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file(options_write):
    target_url = options_write.pop("url")
    repo = options_write.pop("repo")
    package = Package("data/datapackage.json")
    response = package.to_github(target=target_url)
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file_with_bad_credentials(options_write):
    target_url = options_write.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        package = Package("data/datapackage.json")
        package.to_github(target=target_url, control=portals.GithubControl(apikey="test"))
    error = excinfo.value.error
    assert "Bad credentials" in error.message
    assert "Github API error:BadCredentialsException" in error.message


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file_with_no_credentials(options_write):
    target_url = options_write.pop("url")
    with pytest.raises(AssertionError) as excinfo:
        package = Package("data/datapackage.json")
        package.to_github(target=target_url, control=portals.GithubControl(apikey=None))
    assert "AssertionError" in str(excinfo)


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file_with_no_params():
    with pytest.raises(FrictionlessException) as excinfo:
        package = Package("data/datapackage.json")
        package.to_github()
    error = excinfo.value.error
    assert error.message == "Not supported target: None or control"


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
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
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("package.json")) == 'ContentFile(path="package.json")'
    )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_package_file_without_target_url():
    repo = "test-write-without-url"
    package = Package("data/datapackage.json")
    response = package.to_github(control=portals.GithubControl(repo=repo))
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_write_duplicate_repo():
    repo = "test-write-without-url"
    package = Package("data/datapackage.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_github(control=portals.GithubControl(repo=repo))
    error = excinfo.value.error
    assert "Repository creation failed." in error.message
    assert "Github API error:GithubException(" in error.message


# Publish


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "darwin", reason="Fix on MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_github_manager_publish_to_github(options_publish_test_params):
    target_url = options_publish_test_params.pop("url")
    repo = options_publish_test_params.pop("repo")
    package = Package("data/datapackage.json")
    response = package.to_github(target=target_url)
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


# Search


@pytest.mark.vcr
def test_github_manager_catalog_from_empty_repo(options_empty):
    repo_url = options_empty.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(repo_url)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_manager_catalog_from_single_repo(options_with_dp):
    repo_url = options_with_dp.pop("url")
    catalog = Catalog(repo_url)

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[0].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_single_user_multiple_repositories(options_user):
    repo_url = options_user.pop("url")
    # using search because of duplicate packages
    catalog = Catalog(
        repo_url, control=portals.GithubControl(search="'TestAction: Read' in:readme")
    )
    assert len(catalog.packages) == 3
    assert catalog.packages[1].name == "test-tabulator"
    assert catalog.packages[2].name == "test-repo-without-datapackage"


@pytest.mark.vcr
def test_github_manager_catalog_with_search_param_only_containing_userqualifier():
    catalog = Catalog(
        control=portals.GithubControl(search="user:fdtester", per_page=1, page=1),
    )
    assert catalog.packages[0].name == "test-tabulator"
    assert len(catalog.packages[0].resources) == 3
    assert catalog.packages[0].resources[0].name == "first-resource"


@pytest.mark.vcr
def test_github_manager_catalog_with_search_and_user_param():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme", user="fdtester"
        ),
    )
    assert catalog.packages[0].resources[0].name == "capitals"


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
        control=portals.GithubControl(user="fdtester", per_page=1, page=1),
    )
    assert catalog.packages[0].name == "test-tabulator"
    assert len(catalog.packages[0].resources) == 3
    assert catalog.packages[0].resources[0].name == "first-resource"


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
    assert catalog.packages[0].to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_catalog_custom_per_page():
    catalog = Catalog(
        control=portals.GithubControl(
            user="fdtester", search="'TestAction: Read' in:readme", per_page=1, page=1
        ),
    )
    assert len(catalog.packages) == 1
    assert catalog.packages[0].resources[0].name == "capitals"


@pytest.mark.vcr
def test_github_manager_catalog_page():
    catalog = Catalog(
        control=portals.GithubControl(user="fdtester", per_page=1, page=1),
    )
    assert catalog.packages[0].resources[0].name == "first-resource"


@pytest.mark.vcr
def test_github_manager_catalog_with_searchtext_with_no_matches():
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
    assert catalog.packages[0].to_descriptor() == output


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_qualifier():
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated 'TestAction: Read' in:readme", user="fdtester"
        ),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[2].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_param():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme", sort="updated", user="fdtester"
        ),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[2].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_sort_by_updated_in_desc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme",
            sort="updated",
            user="fdtester",
            order="desc",
        ),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[2].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_sort_by_updated_in_asc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme",
            sort="updated",
            user="fdtester",
            order="asc",
        ),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[0].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_by_updated_in_desc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated-desc 'TestAction: Read' in:readme",
            user="fdtester",
            order="desc",
        ),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[2].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_qualifiers_sort_by_updated_in_asc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated-asc 'TestAction: Read' in:readme", user="fdtester"
        ),
    )

    # Read
    expected_file_path = "data/datapackage.json"
    with open(expected_file_path) as file:
        assert catalog.packages[0].to_descriptor() == json.loads(file.read())


@pytest.mark.vcr
def test_github_manager_catalog_bad_url():
    bad_github_url = "https://github.com/test-repo-without-datapackage"
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            bad_github_url,
            control=portals.GithubControl(search="'TestAction: Read' in:readme"),
        )
    error = excinfo.value.error
    assert "Github API errorGithubException" in error.message
