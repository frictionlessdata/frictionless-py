import pytest
import zipfile
import textwrap
from collections.abc import Mapping
from pathlib import Path
from frictionless import Package, Resource, system, helpers
from frictionless import FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_package():
    package = Package("data/package.json")
    assert package.name == "name"
    assert package.basepath == "data"
    assert package.to_descriptor() == {
        "name": "name",
        "resources": [
            {
                "name": "name",
                "path": "table.csv",
            },
        ],
    }


def test_package_from_dict():
    package = Package({"name": "name", "profile": "data-package"})
    assert package.to_descriptor() == {
        "name": "name",
        "profiles": ["data-package"],
    }
    with system.use_standards_version("v1"):
        assert package.to_descriptor() == {
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
    package = Package(NotADict(name="name"))
    assert package.to_descriptor() == {"name": "name"}


def test_package_from_path():
    package = Package("data/package.json")
    assert package.name == "name"
    assert package.basepath == "data"
    assert package.to_descriptor() == {
        "name": "name",
        "resources": [
            {
                "name": "name",
                "path": "table.csv",
            },
        ],
    }


def test_package_from_pathlib():
    package = Package(Path("data/package/datapackage.json"))
    assert len(package.get_resource("data").read_rows()) == 2


def test_package_from_path_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/bad.json")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("bad.json")


def test_package_from_path_error_non_json():
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_descriptor("data/table.csv")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("table.csv")


def test_package_from_path_error_bad_json():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/invalid.json")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("invalid.json")


def test_package_from_path_error_bad_json_not_dict():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/table.json")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("table.json")


@pytest.mark.vcr
def test_package_from_path_remote():
    package = Package(BASEURL % "data/package.json")
    assert package.basepath == BASEURL % "data"
    assert package.to_descriptor() == {
        "name": "name",
        "resources": [{"name": "name", "path": "table.csv"}],
    }


@pytest.mark.vcr
def test_package_from_path_remote_error_not_found():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(BASEURL % "data/bad.json")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("bad.json")


@pytest.mark.vcr
def test_package_from_path_remote_error_bad_json():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(BASEURL % "data/invalid.json")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("invalid.json")


@pytest.mark.vcr
def test_package_from_path_remote_error_bad_json_not_dict():
    with pytest.raises(FrictionlessException) as excinfo:
        Package(BASEURL % "data/table-lists.json")
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("table-lists.json")


def test_package_from_invalid_descriptor_type():
    with pytest.raises(FrictionlessException) as excinfo:
        Package.from_descriptor(51)  # type: ignore
    error = excinfo.value.error
    assert error.type == "package-error"
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
    assert error.type == "package-error"
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
        name="name",
        profiles=["profile"],
        licenses=[],
        sources=[],
        title="title",
        description="description",
        homepage="homepage",
        version="version",
        contributors=[],
        keywords=["keyword"],
        image="image",
        created="created",
        resources=[],
    )
    package = (
        Package(**options)
        if not create_descriptor
        else Package(helpers.create_descriptor(**options))
    )
    assert package.name == "name"
    assert package.profiles == ["profile"]
    assert package.licenses == []
    assert package.sources == []
    assert package.title == "title"
    assert package.description == "description"
    assert package.homepage == "homepage"
    assert package.version == "version"
    assert package.contributors == []
    assert package.keywords == ["keyword"]
    assert package.image == "image"
    assert package.created == "created"
    assert package.resources == []


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


def test_package_pprint():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    package = Package({"resources": [{"name": "name", "data": data}]})
    expected = """
    {'resources': [{'name': 'name',
                    'data': [['id', 'name'], ['1', 'english'], ['2', '中国人']]}]}
    """
    assert repr(package) == textwrap.dedent(expected).strip()


# Bugs


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
