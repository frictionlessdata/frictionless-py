import pytest
from frictionless import Resource, Schema, Detector, FrictionlessException, platform


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


DESCRIPTOR_FK = {
    "path": "data/nested.csv",
    "schema": {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "cat", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "foreignKeys": [{"fields": "cat", "reference": {"resource": "", "fields": "id"}}],
    },
}


def test_resource_schema():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "table.csv",
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_schema_source_data():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "data": [["id", "name"], ["1", "english"], ["2", "中国人"]],
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_schema_source_remote():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "table.csv",
        "schema": "schema.json",
    }
    resource = Resource(descriptor, basepath=BASEURL % "data")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_schema_from_path_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(
            {
                "name": "name",
                "path": "data/table.csv",
                "schema": "data/bad.json",
            }
        )
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.note.count("bad.json")


def test_resource_schema_inferred():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_schema_provided():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "new1", "type": "string"},
                {"name": "new2", "type": "string"},
            ]
        }
    )
    with Resource("data/table.csv", schema=schema) as resource:
        assert resource.labels == ["id", "name"]
        assert resource.header == ["new1", "new2"]
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "new1", "type": "string"},
                {"name": "new2", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"new1": "1", "new2": "english"},
            {"new1": "2", "new2": "中国人"},
        ]


def test_resource_schema_unique():
    source = [["name"], [1], [2], [3]]
    detector = Detector(
        schema_patch={"fields": {"name": {"constraints": {"unique": True}}}}
    )
    with Resource(source, detector=detector) as resource:
        for row in resource.row_stream:
            assert row.valid


def test_resource_schema_unique_error():
    source = [["name"], [1], [2], [2]]
    detector = Detector(
        schema_patch={"fields": {"name": {"constraints": {"unique": True}}}}
    )
    with Resource(source, detector=detector) as resource:
        for row in resource.row_stream:
            if row.row_number == 4:
                assert row.valid is False
                assert row.errors[0].type == "unique-error"
                continue
            assert row.valid


def test_resource_schema_primary_key():
    source = [["name"], [1], [2], [3]]
    detector = Detector(schema_patch={"primaryKey": ["name"]})
    with Resource(source, detector=detector) as resource:
        for row in resource.row_stream:
            assert row.valid


def test_resource_schema_primary_key_error():
    source = [["name"], [1], [2], [2]]
    detector = Detector(schema_patch={"primaryKey": ["name"]})
    with Resource(source, detector=detector) as resource:
        for row in resource.row_stream:
            if row.row_number == 4:
                assert row.valid is False
                assert row.errors[0].type == "primary-key"
                continue
            assert row.valid


def test_resource_schema_foreign_keys():
    resource = Resource(DESCRIPTOR_FK)
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid
    assert rows[3].valid
    assert rows[0].to_dict() == {"id": 1, "cat": None, "name": "England"}
    assert rows[1].to_dict() == {"id": 2, "cat": None, "name": "France"}
    assert rows[2].to_dict() == {"id": 3, "cat": 1, "name": "London"}
    assert rows[3].to_dict() == {"id": 4, "cat": 2, "name": "Paris"}


def test_resource_schema_foreign_keys_invalid():
    resource = Resource(DESCRIPTOR_FK, path="data/nested-invalid.csv")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid
    assert rows[3].valid
    assert rows[4].errors[0].type == "foreign-key"
    assert rows[0].to_dict() == {"id": 1, "cat": None, "name": "England"}
    assert rows[1].to_dict() == {"id": 2, "cat": None, "name": "France"}
    assert rows[2].to_dict() == {"id": 3, "cat": 1, "name": "London"}
    assert rows[3].to_dict() == {"id": 4, "cat": 2, "name": "Paris"}
    assert rows[4].to_dict() == {"id": 5, "cat": 6, "name": "Rome"}
