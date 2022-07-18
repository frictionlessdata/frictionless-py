import os
import pytest
import zipfile
from collections.abc import Mapping
from pathlib import Path
from frictionless import Package, Resource, helpers
from frictionless import FrictionlessException


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_package():
    package = Package("data/package.json")
    assert package.name == "name"
    assert package.basepath == "data"
    assert package.profile == "data-package"
    assert package.resources == [
        {"name": "name", "path": "table.csv"},
    ]


def test_package_from_dict():
    package = Package({"name": "name", "profile": "data-package"})
    assert package == {
        "name": "name",
        "profile": "data-package",
    }


class NotADict(Mapping):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


def test_package_from_mapping():
    package = Package(NotADict(name="name", profile="data-package"))
    assert package == {
        "name": "name",
        "profile": "data-package",
    }


def test_package_from_path():
    package = Package("data/package.json")
    assert package.name == "name"
    assert package.basepath == "data"
    assert package.profile == "data-package"
    assert package.resources == [
        {"name": "name", "path": "table.csv"},
    ]


def test_package_from_pathlib():
    package = Package(Path("data/package/datapackage.json"))
    assert len(package.get_resource("data").read_rows()) == 2


def test_package_from_path_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/bad.json")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("bad.json")


def test_package_from_path_error_non_json():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor="data/table.csv")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("table.csv")


def test_package_from_path_error_bad_json():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/invalid.json")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("invalid.json")


def test_package_from_path_error_bad_json_not_dict():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/table.json")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("table.json")


@pytest.mark.vcr
def test_package_from_path_remote():
    package = Package(BASEURL % "data/package.json")
    assert package.basepath == BASEURL % "data"
    assert package == {
        "name": "name",
        "resources": [{"name": "name", "path": "table.csv"}],
    }


@pytest.mark.vcr
def test_package_from_path_remote_error_not_found():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(BASEURL % "data/bad.json")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("bad.json")


@pytest.mark.vcr
def test_package_from_path_remote_error_bad_json():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(BASEURL % "data/invalid.json")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("invalid.json")


@pytest.mark.vcr
def test_package_from_path_remote_error_bad_json_not_dict():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(BASEURL % "data/table-lists.json")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("table-lists.json")


def test_package_from_invalid_descriptor_type():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor=51)
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("51")


def test_package_from_zip():
    package = Package("data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


@pytest.mark.vcr
def test_package_from_zip_remote():
    package = Package(BASEURL % "data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


def test_package_from_zip_no_descriptor(tmpdir):
    descriptor = str(tmpdir.join("package.zip"))
    with zipfile.ZipFile(descriptor, "w") as zip:
        zip.writestr("data.txt", "foobar")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor)
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("datapackage.json")


def test_package_from_zip_innerpath():
    package = Package("data/innerpath.package.zip", innerpath="datapackage.yaml")
    assert package.name == "emissions"
    assert len(package.resources) == 10


def test_package_from_zip_innerpath_yaml():
    # for issue1174
    package = Package("data/innerpath.package.zip")
    assert package.name == "emissions"
    assert len(package.resources) == 10


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_package_standard_specs_properties(create_descriptor):
    options = dict(
        resources=[],
        name="name",
        id="id",
        licenses=[],
        profile="profile",
        title="title",
        description="description",
        homepage="homepage",
        version="version",
        sources=[],
        contributors=[],
        keywords=["keyword"],
        image="image",
        created="created",
    )
    package = (
        Package(**options)
        if not create_descriptor
        else Package(helpers.create_descriptor(**options))
    )
    assert package.resources == []
    assert package.name == "name"
    assert package.id == "id"
    assert package.licenses == []
    assert package.profile == "profile"
    assert package.title == "title"
    assert package.description == "description"
    assert package.homepage == "homepage"
    assert package.version == "version"
    assert package.sources == []
    assert package.contributors == []
    assert package.keywords == ["keyword"]
    assert package.image == "image"
    assert package.created == "created"


def test_package_description_html():
    package = Package(description="**test**")
    assert package.description == "**test**"
    assert package.description_html == "<p><strong>test</strong></p>"


def test_package_description_html_multiline():
    package = Package(description="**test**\n\nline")
    assert package.description == "**test**\n\nline"
    assert package.description_html == "<p><strong>test</strong></p><p>line</p>"


def test_package_description_text():
    package = Package(description="**test**\n\nline")
    assert package.description == "**test**\n\nline"
    assert package.description_text == "test line"


def test_package_description_text_plain():
    package = Package(description="It's just a plain text. Another sentence")
    assert package.description == "It's just a plain text. Another sentence"
    assert package.description_text == "It's just a plain text. Another sentence"


# Issues


def test_package_dialect_no_header_issue_167():
    package = Package("data/package-dialect-no-header.json")
    resource = package.get_resource("people")
    rows = resource.read_rows()
    assert rows[0]["score"] == 1
    assert rows[1]["score"] == 1


def test_package_validation_is_not_strict_enough_issue_869():
    package = Package("data/issue-869.json")
    errors = package.metadata_errors
    assert len(errors) == 2
    assert errors[0].note == 'property "created" is not valid "datetime"'
    assert errors[1].note == 'property "contributors[].email" is not valid "email"'


def test_package_validation_duplicate_resource_names_issue_942():
    package = Package(
        resources=[
            Resource(name="name", path="data/table.csv"),
            Resource(name="name", path="data/table.csv"),
        ]
    )
    errors = package.metadata_errors
    assert len(errors) == 1
    assert errors[0].note == "names of the resources are not unique"


def test_package_set_hashing():
    package = Package(hashing="SHA-1")
    assert package.hashing == "SHA-1"
    package.hashing = "MD5"
    assert package.hashing == "MD5"


def test_package_set_base_path():
    package = Package(basepath="/data")
    assert package.basepath == "/data"
    package.basepath = "/data/csv"
    assert package.basepath == "/data/csv"


def test_package_set_onerror():
    package = Package(onerror="raise")
    assert package.onerror == "raise"
    package.onerror = "ignore"
    assert package.onerror == "ignore"


def test_package_set_trusted():
    package = Package(trusted=True)
    assert package.trusted is True
    package.trusted = False
    assert package.trusted is False


def test_package_pprint_1029():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    package = Package({"resources": [{"name": "name", "data": data}]})
    expected = """{'resources': [{'data': [['id', 'name'], ['1', 'english'], ['2', '中国人']],
                'name': 'name'}]}"""
    assert repr(package) == expected


def test_package_to_erd_1118(tmpdir):
    package = Package("data/package-storage.json")
    output_file = os.path.join(tmpdir, "output.dot")
    with open("data/fixtures/dot-files/package.dot") as file:
        expected = file.read()
    package.to_er_diagram(output_file)
    with open(output_file) as file:
        output = file.read()
    assert expected.strip() == output.strip()


def test_package_to_erd_table_names_with_dash_1118(tmpdir):
    # graphviz shows error if the table/field name has "-" so need to
    # wrap names with quotes ""
    package = Package("data/datapackage.json")
    output_file = os.path.join(tmpdir, "output.dot")
    with open(
        "data/fixtures/dot-files/package-resource-names-including-dash.dot"
    ) as file:
        expected = file.read()
    package.to_er_diagram(output_file)
    with open(output_file) as file:
        output = file.read()
    assert expected.strip() == output.strip()
    assert output.count('"number-two"')


def test_package_to_erd_without_table_relationships_1118(tmpdir):
    package = Package("data/datapackage.json")
    output_file = os.path.join(tmpdir, "output.dot")
    with open(
        "data/fixtures/dot-files/package-resource-names-including-dash.dot"
    ) as file:
        expected = file.read()
    package.to_er_diagram(output_file)
    with open(output_file) as file:
        output = file.read()
    assert expected.strip() == output.strip()
    assert output.count("->") == 0
