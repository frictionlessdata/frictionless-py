import os
import json
import yaml
import pytest
import zipfile
from pathlib import Path
from frictionless import Package, Resource, Layout, describe_package, helpers
from frictionless import FrictionlessException
from frictionless.plugins.sql import SqlDialect


# General


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


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


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
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
@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_from_zip_remote():
    package = Package(BASEURL % "data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_from_zip_no_descriptor(tmpdir):
    descriptor = str(tmpdir.join("package.zip"))
    with zipfile.ZipFile(descriptor, "w") as zip:
        zip.writestr("data.txt", "foobar")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor)
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note.count("datapackage.json")


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


# Resources


def test_package_resources():
    package = Package("data/package.json")
    assert package.name == "name"
    assert package.basepath == "data"
    assert package.profile == "data-package"
    assert package.resources == [
        {"name": "name", "path": "table.csv"},
    ]


def test_package_resources_inline():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    package = Package({"resources": [{"name": "name", "data": data}]})
    resource = package.get_resource("name")
    assert len(package.resources) == 1
    assert resource.path is None
    assert resource.data == data
    assert resource.fullpath is None
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_resources_empty():
    package = Package()
    assert package.resources == []


def test_package_add_resource():
    package = Package({})
    resource = package.add_resource({"name": "name", "data": []})
    assert len(package.resources) == 1
    assert package.resources[0].name == "name"
    assert resource.name == "name"


def test_package_get_resource():
    package = Package("data/package/datapackage.json")
    resource = package.get_resource("data")
    assert resource.name == "data"


def test_package_get_resource_error_not_found():
    package = Package("data/package/datapackage.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.get_resource("bad")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note == 'resource "bad" does not exist'


def test_package_remove_resource():
    package = Package("data/package/datapackage.json")
    resource = package.remove_resource("data")
    assert package.resource_names == ["data2"]
    assert resource.name == "data"


def test_package_remove_resource_error_not_found():
    package = Package("data/package/datapackage.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.remove_resource("bad")
    error = excinfo.value.error
    assert error.code == "package-error"
    assert error.note == 'resource "bad" does not exist'


def test_package_update_resource():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    package = Package({"resources": [{"name": "name", "data": data}]})
    resource = package.get_resource("name")
    resource.name = "newname"
    assert package == {"resources": [{"name": "newname", "data": data}]}


def test_package_resources_append_in_place():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    package = Package({"resources": []})
    package.resources.append({"name": "newname", "data": data})
    assert package == {"resources": [{"name": "newname", "data": data}]}


def test_package_resources_remove_in_place():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    package = Package({"resources": [{"name": "newname", "data": data}]})
    del package.resources[0]
    assert package == {"resources": []}


def test_package_resources_respect_layout_set_after_creation_issue_503():
    package = Package(resources=[Resource(path="data/table.csv")])
    resource = package.get_resource("table")
    resource.layout = Layout(limit_rows=1)
    assert resource.read_rows() == [{"id": 1, "name": "english"}]
    assert resource.header == ["id", "name"]


# Compression


def test_package_compression_implicit_gz():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("implicit-gz")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_compression_implicit_zip():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("implicit-zip")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_compression_explicit_gz():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("explicit-gz")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_compression_explicit_zip():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("explicit-zip")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


# Schema


DESCRIPTOR_FK = {
    "resources": [
        {
            "name": "main",
            "data": [
                ["id", "name", "surname", "parent_id"],
                ["1", "Alex", "Martin", ""],
                ["2", "John", "Dockins", "1"],
                ["3", "Walter", "White", "2"],
            ],
            "schema": {
                "fields": [
                    {"name": "id"},
                    {"name": "name"},
                    {"name": "surname"},
                    {"name": "parent_id"},
                ],
                "foreignKeys": [
                    {
                        "fields": "name",
                        "reference": {"resource": "people", "fields": "firstname"},
                    },
                ],
            },
        },
        {
            "name": "people",
            "data": [
                ["firstname", "surname"],
                ["Alex", "Martin"],
                ["John", "Dockins"],
                ["Walter", "White"],
            ],
        },
    ],
}


def test_package_schema_foreign_key():
    package = Package(DESCRIPTOR_FK)
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid
    assert rows[0].to_dict() == {
        "id": "1",
        "name": "Alex",
        "surname": "Martin",
        "parent_id": None,
    }
    assert rows[1].to_dict() == {
        "id": "2",
        "name": "John",
        "surname": "Dockins",
        "parent_id": "1",
    }
    assert rows[2].to_dict() == {
        "id": "3",
        "name": "Walter",
        "surname": "White",
        "parent_id": "2",
    }


def test_package_schema_foreign_key_invalid():
    package = Package(DESCRIPTOR_FK)
    package.resources[1].data[3][0] = "bad"
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].errors[0].code == "foreign-key-error"
    assert rows[0].to_dict() == {
        "id": "1",
        "name": "Alex",
        "surname": "Martin",
        "parent_id": None,
    }
    assert rows[1].to_dict() == {
        "id": "2",
        "name": "John",
        "surname": "Dockins",
        "parent_id": "1",
    }
    assert rows[2].to_dict() == {
        "id": "3",
        "name": "Walter",
        "surname": "White",
        "parent_id": "2",
    }


def test_package_schema_foreign_key_self_reference():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].schema.foreign_keys = [
        {"fields": "parent_id", "reference": {"resource": "", "fields": "id"}}
    ]
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid


def test_package_schema_foreign_key_self_reference_invalid():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].data[2][0] = "0"
    package.resources[0].schema.foreign_keys = [
        {"fields": "parent_id", "reference": {"resource": "", "fields": "id"}}
    ]
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].errors[0].code == "foreign-key-error"


def test_package_schema_foreign_key_multifield():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].schema.foreign_keys = [
        {
            "fields": ["name", "surname"],
            "reference": {"resource": "people", "fields": ["firstname", "surname"]},
        }
    ]
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid


def test_package_schema_foreign_key_multifield_invalid():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].schema.foreign_keys = [
        {
            "fields": ["name", "surname"],
            "reference": {"resource": "people", "fields": ["firstname", "surname"]},
        }
    ]
    package.resources[1].data[3][0] = "bad"
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].errors[0].code == "foreign-key-error"


# Onerror


def test_resource_onerror():
    package = Package(resources=[Resource(path="data/invalid.csv")])
    resource = package.resources[0]
    assert package.onerror == "ignore"
    assert resource.onerror == "ignore"
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="warn")
    resource = package.resources[0]
    assert package.onerror == "warn"
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    package = Package({"resources": [{"data": data, "schema": schema}]}, onerror="raise")
    resource = package.resources[0]
    assert package.onerror == "raise"
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="warn")
    resource = package.resources[0]
    assert package.onerror == "warn"
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    package = Package({"resources": [{"data": data, "schema": schema}]}, onerror="raise")
    resource = package.resources[0]
    assert package.onerror == "raise"
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


# Expand


def test_package_expand():
    package = Package("data/package.json")
    package.expand()
    assert package == {
        "name": "name",
        "profile": "data-package",
        "resources": [{"name": "name", "path": "table.csv", "profile": "data-resource"}],
    }


def test_package_expand_empty():
    package = Package()
    package.expand()
    assert package == {
        "profile": "data-package",
        "resources": [],
    }


def test_package_expand_resource_schema():
    schema = {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }
    package = Package({"resources": [{"path": "data/table.csv", "schema": schema}]})
    package.expand()
    assert package == {
        "resources": [
            {
                "path": "data/table.csv",
                "schema": {
                    "fields": [
                        {
                            "name": "id",
                            "type": "integer",
                            "format": "default",
                            "bareNumber": True,
                        },
                        {"name": "name", "type": "string", "format": "default"},
                    ],
                    "missingValues": [""],
                },
                "profile": "data-resource",
            }
        ],
        "profile": "data-package",
    }


def test_package_expand_resource_dialect():
    dialect = {"delimiter": ";"}
    package = Package({"resources": [{"path": "data/table.csv", "dialect": dialect}]})
    package.expand()
    assert package == {
        "resources": [
            {
                "path": "data/table.csv",
                "dialect": {
                    "delimiter": ";",
                    "lineTerminator": "\r\n",
                    "quoteChar": '"',
                    "doubleQuote": True,
                    "skipInitialSpace": False,
                },
                "profile": "data-resource",
            }
        ],
        "profile": "data-package",
    }


# Infer


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_infer():
    package = Package("data/infer/*.csv")
    package.infer(stats=True)
    assert package.metadata_valid
    assert package == {
        "profile": "data-package",
        "resources": [
            {
                "path": "data/infer/data.csv",
                "profile": "tabular-data-resource",
                "name": "data",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "description", "type": "string"},
                        {"name": "amount", "type": "number"},
                    ]
                },
                "stats": {
                    "hash": "c028f525f314c49ea48ed09e82292ed2",
                    "bytes": 114,
                    "fields": 4,
                    "rows": 2,
                },
            },
            {
                "path": "data/infer/data2.csv",
                "profile": "tabular-data-resource",
                "name": "data2",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "schema": {
                    "fields": [
                        {"name": "parent", "type": "string"},
                        {"name": "comment", "type": "string"},
                    ]
                },
                "stats": {
                    "hash": "cb4a683d8eecb72c9ac9beea91fd592e",
                    "bytes": 60,
                    "fields": 2,
                    "rows": 3,
                },
            },
        ],
    }


def test_package_infer_with_basepath():
    package = Package("*.csv", basepath="data/infer")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 2
    assert package.resources[0].path == "data.csv"
    assert package.resources[1].path == "data2.csv"


def test_package_infer_multiple_paths():
    package = Package(["data.csv", "data2.csv"], basepath="data/infer")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 2
    assert package.resources[0].path == "data.csv"
    assert package.resources[1].path == "data2.csv"


def test_package_infer_non_utf8_file():
    package = Package("data/table-with-accents.csv")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 1
    assert package.resources[0].encoding == "iso8859-1"


def test_package_infer_empty_file():
    package = Package("data/empty.csv")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 1
    assert package.resources[0].stats["bytes"] == 0


def test_package_infer_duplicate_resource_names_issue_530():
    package = Package(
        resources=[
            Resource(path="data/chunk1.csv"),
            Resource(path="data/chunk2.csv"),
            Resource(path="data/tables/chunk1.csv"),
            Resource(path="data/tables/chunk2.csv"),
        ]
    )
    package.infer()
    assert len(set(package.resource_names)) == 4
    assert package.resource_names == ["chunk1", "chunk2", "chunk12", "chunk22"]


# Import/Export


def test_package_to_copy():
    source = describe_package("data/chunk*.csv")
    target = source.to_copy()
    assert source is not target
    assert source == target


def test_package_to_json(tmpdir):

    # Write
    target = os.path.join(tmpdir, "package.json")
    package = Package("data/package.json")
    package.to_json(target)

    # Read
    with open(target, encoding="utf-8") as file:
        assert package == json.load(file)


def test_package_to_yaml(tmpdir):

    # Write
    target = os.path.join(tmpdir, "package.yaml")
    package = Package("data/package.json")
    package.to_yaml(target)

    # Read
    with open(target, encoding="utf-8") as file:
        assert package == yaml.safe_load(file)


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package("data/package.json")
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.name == "name"
    assert target.get_resource("name").name == "name"
    assert target.get_resource("name").path == "table.csv"
    assert target.get_resource("name").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip_resource_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path="data/table.csv")])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == "data/table.csv"
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip_resource_absolute_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path=os.path.abspath("data/table.csv"))])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == "table.csv"
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip_resource_remote_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path=BASEURL % "data/table.csv")])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == BASEURL % "data/table.csv"
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip_resource_memory_inline(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    data = [["id", "name"], [1, "english"], [2, "中国人"]]
    source = Package(resources=[Resource(name="table", data=data)])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").data == data
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip_resource_memory_function(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    data = lambda: [["id", "name"], [1, "english"], [2, "中国人"]]
    source = Package(resources=[Resource(name="table", data=data)])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == 'table.csv'
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_package_to_zip_resource_sql(tmpdir, database_url):
    path = os.path.join(tmpdir, "package.zip")
    dialect = SqlDialect(table="table")
    source = Package(resources=[Resource(database_url, name='table', dialect=dialect)])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == database_url
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


# Issues


def test_package_dialect_no_header_issue_167():
    package = Package("data/package-dialect-no-header.json")
    resource = package.get_resource("people")
    rows = resource.read_rows()
    assert rows[0]["score"] == 1
    assert rows[1]["score"] == 1
