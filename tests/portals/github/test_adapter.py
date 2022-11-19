# type: ignore
import os
import pytest
from frictionless import portals, Catalog, Package, FrictionlessException, platform


OUTPUT_OPTIONS_WITH_DP_YAML = {
    "resources": [
        {
            "name": "capitals",
            "type": "table",
            "path": "data/capitals.csv",
            "scheme": "file",
            "format": "csv",
            "encoding": "utf-8",
            "mediatype": "text/csv",
            "dialect": {"csv": {"skipInitialSpace": True}},
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "cid", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
        }
    ]
}
OUTPUT_OPTIONS_WITH_DP = {
    "name": "test-package",
    "resources": [
        {
            "name": "first-resource",
            "path": "table.xls",
            "schema": {
                "fields": [
                    {"name": "id", "type": "number"},
                    {"name": "name", "type": "string"},
                ]
            },
        }
    ],
}

OUTPUT_OPTIONS_WITHOUT_DP_CSV = {
    "name": "test-repo-without-datapackage",
    "resources": [
        {
            "name": "capitals",
            "type": "table",
            "path": "data/capitals.csv",
            "scheme": "https",
            "format": "csv",
            "mediatype": "text/csv",
        },
        {
            "name": "countries",
            "type": "table",
            "path": "data/countries.csv",
            "scheme": "https",
            "format": "csv",
            "mediatype": "text/csv",
        },
    ],
}
OUTPUT_OPTIONS_WITHOUT_DP = {
    "name": "test-repo-without-datapackage",
    "resources": [
        {
            "name": "capitals",
            "type": "table",
            "path": "data/capitals.csv",
            "scheme": "https",
            "format": "csv",
            "mediatype": "text/csv",
        },
        {
            "name": "countries",
            "type": "table",
            "path": "data/countries.csv",
            "scheme": "https",
            "format": "csv",
            "mediatype": "text/csv",
        },
        {
            "name": "student",
            "type": "table",
            "path": "data/student.xlsx",
            "scheme": "https",
            "format": "xlsx",
            "mediatype": "application/vnd.ms-excel",
        },
    ],
}


# Read


@pytest.mark.vcr
def test_github_adapter_read(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP
    assert (
        package.resources[0].basepath
        == "https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master"
    )


@pytest.mark.vcr
def test_github_adapter_read_without_apikey(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url, control=portals.GithubControl(apikey=None))
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


@pytest.mark.vcr
def test_github_adapter_read_repo_with_datapackage(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITH_DP
    assert (
        package.resources[0].basepath
        == "https://raw.githubusercontent.com/fdtester/test-repo-with-datapackage-json/master"
    )


@pytest.mark.vcr
def test_github_adapter_read_no_datapackage_found(options_empty):
    url = options_empty.pop("url")
    control = portals.GithubControl()
    with pytest.raises(FrictionlessException) as excinfo:
        Package(url, control=control)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_adapter_read_default(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.GithubControl()
    package = Package(url, control=control)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


@pytest.mark.vcr
def test_github_adapter_read_other_file_types(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.GithubControl(formats=["csv"])
    package = Package(url, control=control)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP_CSV


@pytest.mark.vcr
def test_github_adapter_read_with_url_and_control(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.GithubControl(formats=["xlsx"])
    package = Package(url, control=control)
    assert package.to_descriptor() == {
        "name": "test-repo-without-datapackage",
        "resources": [
            {
                "name": "student",
                "type": "table",
                "path": "data/student.xlsx",
                "scheme": "https",
                "format": "xlsx",
                "mediatype": "application/vnd.ms-excel",
            }
        ],
    }


# TODO: recover
@pytest.mark.skip
@pytest.mark.vcr
def test_github_adapter_read_with_wrongurl():
    url = "test"
    with pytest.raises(FrictionlessException) as excinfo:
        Package(url, control=portals.GithubControl())
    error = excinfo.value.error
    assert error.message == "Not supported Github source 'test' or control"


@pytest.mark.vcr
def test_github_adapter_read_without_url_with_controls(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    package = Package(control=portals.GithubControl(user=user, repo=repo))
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


@pytest.mark.vcr
def test_github_adapter_alias(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


@pytest.mark.vcr
def test_github_adapter_alias_read_custom_file_types(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.GithubControl(formats=["csv"])
    package = Package(url, control=control)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP_CSV


@pytest.mark.vcr
def test_github_adapter_alias_without_url_with_controls(options_without_dp):
    user = options_without_dp.pop("user")
    repo = options_without_dp.pop("repo")
    package = Package(control=portals.GithubControl(user=user, repo=repo))
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


def test_github_adapter_read_without_repo_user():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(control=portals.GithubControl())
    error = excinfo.value.error
    assert error.message == "Repo and user is required"


@pytest.mark.vcr
def test_github_adapter_read_yaml(options_with_dp_yaml):
    url = options_with_dp_yaml.pop("url")
    package = Package(url)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITH_DP_YAML


@pytest.mark.vcr
def test_github_adapter_read_resource_with_duplicate_packages(
    options_with_duplicate_files,
):
    url = options_with_duplicate_files.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(url)
    error = excinfo.value.error
    assert (
        error.message
        == 'The data package has an error: resource "table-reverse" already exists'
    )


@pytest.mark.vcr
def test_github_adapter_read_resources(options_with_dp):
    url = options_with_dp.pop("url")
    packages = Package(url)
    assert len(packages.resources) == 2
    assert packages.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_package_with_files_in_multiple_folders(
    options_with_multiple_folders,
):
    url = options_with_multiple_folders.pop("url")
    packages = Package(url)
    assert len(packages.resources) == 3
    assert packages.resources[0].name == "first-resource"
    assert packages.resources[1].name == "number-two"
    assert packages.resources[2].name == "countries"


@pytest.mark.vcr
def test_github_adapter_read_resources_without_dp(options_without_dp):
    url = options_without_dp.pop("url")
    packages = Package(url)
    assert len(packages.resources) == 3
    assert packages.resources[0].name == "capitals"
    assert packages.resources[0].path == "data/capitals.csv"


# Read - Data


@pytest.mark.vcr
def test_github_adapter_read_data_csv_files_in_different_folder_():
    package = Package("https://github.com/fdtester/test-repo-with-datapackage-yaml")
    package.resources[0].read_rows() == [
        {"id": 1, "cid": 1, "name": "London"},
        {"id": 2, "cid": 2, "name": "Paris"},
        {"id": 3, "cid": 3, "name": "Berlin"},
        {"id": 4, "cid": 4, "name": "Rome"},
        {"id": 5, "cid": 5, "name": "Lisbon"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_data_from_ods():
    package = Package("https://github.com/fdtester/test-repo-with-ods-data-file")
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_data_from_repo_with_datapackage(
    options_with_dp,
):
    url = options_with_dp.pop("url")
    package = Package(url)
    assert package.to_descriptor() == OUTPUT_OPTIONS_WITH_DP
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_data_from_repo_with_http_data_csv():
    package = Package(
        "https://github.com/fdtester/test-repo-resources-with-http-data-csv"
    )
    assert package.resources[0].read_rows() == [
        {"id": 1, "cid": "1", "name": "London"},
        {"id": 2, "cid": "2", "name": "Paris"},
        {"id": 3, "cid": "3", "name": "Berlin"},
        {"id": 4, "cid": "4", "name": "Rome"},
        {"id": 5, "cid": "5", "name": "Lisbon"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_data_from_repo_with_http_data_xls():
    package = Package(
        "https://github.com/fdtester/test-repo-resources-with-http-data-xls"
    )
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_data_from_repo_with_inline_data():
    package = Package("https://github.com/fdtester/test-repo-resources-with-inline-data")
    assert package.resources[0].read_rows() == [
        {"name": "Alex", "age": 33},
        {"name": "Paul", "age": 44},
    ]


@pytest.mark.vcr
def test_github_adapter_read_data_ndjson():
    package = Package("https://github.com/fdtester/test-repo-resources-with-json-data")
    assert package.resources[0].read_rows() == [
        {"id": 1, "name of language": "english"},
        {"id": 2, "name of language": "中国人"},
    ]
    assert package.resources[1].read_rows() == [
        {"id": 1, "name of language": "english"},
        {"id": 2, "name of language": "中国人"},
    ]


@pytest.mark.vcr
def test_github_adapter_read_without_resource_file():
    package = Package("https://github.com/fdtester/test-repo-without-resources-file")
    with pytest.raises(FrictionlessException) as excinfo:
        package.resources[0].read_rows()
    error = excinfo.value.error
    assert (
        "The data source could not be successfully loaded: 404 Client Error"
        in error.message
    )


@pytest.mark.vcr
def test_github_adapter_read_invalid_package():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("https://github.com/fdtester/test-repo-with-invalid-package")
    error = excinfo.value.error
    assert "The data package has an error: descriptor is not valid" in error.message


@pytest.mark.vcr
def test_github_adapter_read_data_check_path_is_valid():
    package = Package("https://github.com/fdtester/test-repo-with-datapackage-json")
    assert package.resources[0].path == "table.xls"


@pytest.mark.vcr
def test_github_adapter_read_data_using_to_view():
    package = Package("https://github.com/fdtester/test-repo-resources-with-inline-data")
    assert package.resources[0].read_rows() == [
        {"name": "Alex", "age": 33},
        {"name": "Paul", "age": 44},
    ]


# Write


@pytest.mark.vcr
def test_github_adapter_write_package_file_with_descriptor_empty_resources():
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
    response = package.publish(control=portals.GithubControl(user="fdtester", repo=repo))
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
def test_github_adapter_write_package_file_with_descriptor():
    repo = "test-write-package-with-descriptor"
    descriptor = {"name": "test-tabulator", "resources": []}
    package = Package(descriptor)
    response = package.publish(control=portals.GithubControl(user="fdtester", repo=repo))
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
def test_github_adapter_write_package_file(options_write):
    target_url = options_write.pop("url")
    repo = options_write.pop("repo")
    package = Package("data/datapackage.json")
    response = package.publish(target=target_url)
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
def test_github_adapter_write_package_file_with_bad_credentials(options_write):
    target_url = options_write.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        package = Package("data/datapackage.json")
        package.publish(target=target_url, control=portals.GithubControl(apikey="test"))
    error = excinfo.value.error
    assert "Bad credentials" in error.message
    assert "Github API error:BadCredentialsException" in error.message


@pytest.mark.vcr
def test_github_adapter_write_package_file_with_no_credentials(options_write):
    target_url = options_write.pop("url")
    with pytest.raises(AssertionError) as excinfo:
        package = Package("data/datapackage.json")
        package.publish(target=target_url, control=portals.GithubControl(apikey=None))
    assert "AssertionError" in str(excinfo)


@pytest.mark.vcr
def test_github_adapter_write_package_file_with_no_params():
    with pytest.raises(FrictionlessException) as excinfo:
        package = Package("data/datapackage.json")
        package.publish()
    error = excinfo.value.error
    assert error.message == "Not supported target: None or control"


@pytest.mark.vcr
def test_github_adapter_write_package_file_with_additional_params(
    options_write_test_params,
):
    target_url = options_write_test_params.pop("url")
    repo = options_write_test_params.pop("repo")
    package = Package("data/datapackage.json")
    response = package.publish(
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
def test_github_adapter_write_package_file_without_target_url():
    repo = "test-write-without-url"
    package = Package("data/datapackage.json")
    response = package.publish(control=portals.GithubControl(repo=repo))
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
def test_github_adapter_write_duplicate_repo():
    repo = "test-write-without-url"
    package = Package("data/datapackage.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.publish(control=portals.GithubControl(repo=repo))
    error = excinfo.value.error
    assert "Repository creation failed." in error.message
    assert "Github API error:GithubException(" in error.message


# Publish


@pytest.mark.vcr
def test_github_adapter_publish_to_github(options_publish_test_params):
    target_url = options_publish_test_params.pop("url")
    repo = options_publish_test_params.pop("repo")
    package = Package("data/datapackage.json")
    response = package.publish(target=target_url)
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )


@pytest.mark.vcr
def test_github_adapter_publish_to_github_multiple_folders():
    repo = "test-write-to-multiple-folders"
    package = Package("data/multiple-folders.package.json")
    response = package.publish(
        control=portals.GithubControl(
            email="frictionlessdata@okfn.org", user="fdtester", repo=repo
        )
    )
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )
    assert (
        repr(response.get_contents("package/data.csv"))
        == 'ContentFile(path="package/data.csv")'
    )
    assert (
        repr(response.get_contents("countries.csv"))
        == 'ContentFile(path="countries.csv")'
    )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "windows", reason="Path Error on Windows")
def test_github_adapter_publish_to_github_multiple_folders_with_basepath():
    repo = "test-write-to-multiple-folders-with-basepath"
    package_file_path = os.path.join("data", "multiple-folders.package.json")
    package = Package(package_file_path)
    response = package.publish(
        control=portals.GithubControl(
            email="frictionlessdata@okfn.org",
            user="fdtester",
            repo=repo,
            basepath="fd-data",
        )
    )
    assert response.url == f"https://api.github.com/repos/fdtester/{repo}"
    assert (
        repr(response.get_contents("fd-data/datapackage.json"))
        == 'ContentFile(path="fd-data/datapackage.json")'
    )
    assert (
        repr(response.get_contents("fd-data/package/data.csv"))
        == 'ContentFile(path="fd-data/package/data.csv")'
    )
    assert (
        repr(response.get_contents("fd-data/countries.csv"))
        == 'ContentFile(path="fd-data/countries.csv")'
    )


@pytest.mark.vcr
def test_github_adapter_publish_package_read_from_github_repo_with_data_package():
    repo_to_write = "test-write-package-read-from-github"
    package = Package("https://github.com/fdtester/test-repo-with-datapackage-json")
    control = portals.GithubControl(repo=repo_to_write)
    response = package.publish(control=control)
    assert response.url == f"https://api.github.com/repos/fdtester/{repo_to_write}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )
    assert repr(response.get_contents("table.xls")) == 'ContentFile(path="table.xls")'


@pytest.mark.ci
@pytest.mark.vcr
def test_github_adapter_publish_package_read_from_github_repo_without_data_package():
    repo_to_write = "test-write-package-read-from-github-repo-without-datapackage"
    package = Package("https://github.com/fdtester/test-repo-without-datapackage")
    control = portals.GithubControl(repo=repo_to_write)
    response = package.publish(control=control)
    assert response.url == f"https://api.github.com/repos/fdtester/{repo_to_write}"
    assert (
        repr(response.get_contents("datapackage.json"))
        == 'ContentFile(path="datapackage.json")'
    )
    assert (
        repr(response.get_contents("data/capitals.csv"))
        == 'ContentFile(path="data/capitals.csv")'
    )
    assert (
        repr(response.get_contents("data/countries.csv"))
        == 'ContentFile(path="data/countries.csv")'
    )
    assert (
        repr(response.get_contents("data/student.xlsx"))
        == 'ContentFile(path="data/student.xlsx")'
    )


# Search


@pytest.mark.vcr
def test_github_adapter_catalog_from_empty_repo(options_empty):
    repo_url = options_empty.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(repo_url)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_adapter_catalog_from_single_repo(options_with_dp):
    repo_url = options_with_dp.pop("url")
    catalog = Catalog(repo_url)
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_from_single_repo_multiple_packages():
    catalog = Catalog("https://github.com/fdtester/test-repo-with-multiple-packages")
    assert len(catalog.packages) == 2
    assert catalog.packages[0].name == "package-fddata-1"
    assert catalog.packages[1].name == "package-fddata-2"
    assert catalog.packages[0].resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    assert catalog.packages[1].resources[0].read_rows() == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


@pytest.mark.vcr
def test_github_adapter_catalog_from_single_repo_multiple_packages_different_folder():
    catalog = Catalog("https://github.com/fdtester/test-repo-with-multiple-packages")
    assert len(catalog.packages) == 2
    assert catalog.packages[0].resources[0].path == "data/table.xls"
    assert catalog.packages[1].resources[0].path == "countries.csv"


@pytest.mark.vcr
def test_github_adapter_catalog_single_user_multiple_repositories(options_user):
    repo_url = options_user.pop("url")
    # using search because of duplicate packages
    catalog = Catalog(
        repo_url, control=portals.GithubControl(search="'TestAction: Read' in:readme")
    )
    assert len(catalog.packages) == 3
    assert catalog.packages[1].name == "test-tabulator"
    assert catalog.packages[2].name == "test-repo-without-datapackage"


@pytest.mark.vcr
def test_github_adapter_catalog_with_search_param_only_containing_userqualifier():
    catalog = Catalog(
        control=portals.GithubControl(search="user:fdtester", per_page=1, page=1),
    )
    assert catalog.packages[0].name == "test-tabulator"
    assert len(catalog.packages[0].resources) == 3
    assert catalog.packages[0].resources[0].name == "first-resource"


@pytest.mark.vcr
def test_github_adapter_catalog_with_search_and_user_param():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme", user="fdtester"
        ),
    )
    assert catalog.packages[0].resources[0].name == "capitals"


@pytest.mark.ci
@pytest.mark.vcr
def test_github_adapter_catalog_with_search_text_and_without_user_or_userqualifier():
    catalog = Catalog(
        control=portals.GithubControl(search="frictionlessdata", per_page=2, page=1),
    )
    assert catalog.packages[0].name == "schemas"
    assert catalog.packages[1].name == "fellows"


@pytest.mark.vcr
def test_github_adapter_catalog_with_user_param_only():
    catalog = Catalog(
        control=portals.GithubControl(user="fdtester", per_page=1, page=1),
    )
    assert catalog.packages[0].name == "test-tabulator"
    assert len(catalog.packages[0].resources) == 3
    assert catalog.packages[0].resources[0].name == "first-resource"


@pytest.mark.vcr
def test_github_adapter_catalog_with_repo_param_only():
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            control=portals.GithubControl(repo="test-repo-without-datapackage"),
        )
    error = excinfo.value.error
    assert "invalid" in error.message
    assert "Github API errorGithubException" in error.message


@pytest.mark.vcr
def test_github_adapter_catalog_without_search_user_repo_params():
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            control=portals.GithubControl(),
        )
    error = excinfo.value.error
    assert error.message == "Repo or user or search text is required"


@pytest.mark.vcr
def test_github_adapter_catalog_with_full_path_repo_only():
    catalog = Catalog(
        control=portals.GithubControl(repo="fdtester/test-repo-without-datapackage"),
    )
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


@pytest.mark.vcr
def test_github_adapter_catalog_custom_per_page():
    catalog = Catalog(
        control=portals.GithubControl(
            user="fdtester", search="'TestAction: Read' in:readme", per_page=1, page=1
        ),
    )
    assert len(catalog.packages) == 1
    assert catalog.packages[0].resources[0].name == "capitals"


@pytest.mark.vcr
def test_github_adapter_catalog_page():
    catalog = Catalog(
        control=portals.GithubControl(user="fdtester", per_page=1, page=1),
    )
    assert catalog.packages[0].resources[0].name == "first-resource"


@pytest.mark.vcr
def test_github_adapter_catalog_with_searchtext_with_no_matches():
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            control=portals.GithubControl(search="user:fdtester test-repo-empty"),
        )
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_github_adapter_catalog_qualifiers():
    catalog = Catalog(
        control=portals.GithubControl(
            search="Frictionlessdata in:readme", user="fdtester"
        ),
    )
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITHOUT_DP


@pytest.mark.vcr
def test_github_adapter_catalog_qualifiers_sort_qualifier():
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated 'TestAction: Read' in:readme", user="fdtester"
        ),
    )
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_qualifiers_sort_param():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme", sort="updated", user="fdtester"
        ),
    )
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_sort_by_updated_in_desc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme",
            sort="updated",
            user="fdtester",
            order="desc",
        ),
    )
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_sort_by_updated_in_asc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="'TestAction: Read' in:readme",
            sort="updated",
            user="fdtester",
            order="asc",
        ),
    )
    assert catalog.packages[3].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_qualifiers_sort_by_updated_in_desc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated-desc 'TestAction: Read' in:readme",
            user="fdtester",
            order="desc",
        ),
    )
    assert catalog.packages[0].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_qualifiers_sort_by_updated_in_asc_order():
    catalog = Catalog(
        control=portals.GithubControl(
            search="sort:updated-asc 'TestAction: Read' in:readme", user="fdtester"
        ),
    )
    assert catalog.packages[3].to_descriptor() == OUTPUT_OPTIONS_WITH_DP


@pytest.mark.vcr
def test_github_adapter_catalog_bad_url():
    bad_github_url = "https://github.com/test-repo-without-datapackage"
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(
            bad_github_url,
            control=portals.GithubControl(search="'TestAction: Read' in:readme"),
        )
    error = excinfo.value.error
    assert "Github API errorGithubException" in error.message
