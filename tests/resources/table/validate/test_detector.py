from frictionless import Resource, Dialect, Schema, Detector


# General


def test_resource_validate_detector_sync_schema():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
        }
    )
    detector = Detector(schema_sync=True)
    resource = Resource("data/sync-schema.csv", schema=schema, detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "id", "type": "integer"},
        ],
    }


def test_resource_validate_detector_sync_schema_invalid():
    source = [["LastName", "FirstName", "Address"], ["Test", "Tester", "23 Avenue"]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "FirstName", "type": "string"},
                {"name": "LastName", "type": "string"},
            ]
        }
    )
    detector = Detector(schema_sync=True)
    resource = Resource(source, schema=schema, detector=detector)
    report = resource.validate()
    assert report.valid


def test_resource_validate_detector_headers_errors():
    source = [
        ["id", "last_name", "first_name", "language"],
        [1, "Alex", "John", "English"],
        [2, "Peters", "John", "Afrikaans"],
        [3, "Smith", "Paul", None],
    ]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "number"},
                {"name": "language", "type": "string", "constraints": {"required": True}},
                {"name": "country", "type": "string"},
            ]
        }
    )
    detector = Detector(schema_sync=True)
    resource = Resource(source, schema=schema, detector=detector)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [4, 4, "constraint-error", ["3", "Smith", "Paul", ""]],
    ]


def test_resource_validate_detector_patch_schema():
    detector = Detector(schema_patch={"missingValues": ["-"]})
    resource = Resource("data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "missingValues": ["-"],
    }


def test_resource_validate_detector_patch_schema_fields():
    detector = Detector(
        schema_patch={"fields": {"id": {"type": "string"}}, "missingValues": ["-"]}
    )
    resource = Resource("data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "id", "type": "string"}, {"name": "name", "type": "string"}],
        "missingValues": ["-"],
    }


def test_resource_validate_detector_infer_type_string():
    detector = Detector(field_type="string")
    resource = Resource("data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "id", "type": "string"}, {"name": "name", "type": "string"}],
    }


def test_resource_validate_detector_infer_type_any():
    detector = Detector(field_type="any")
    resource = Resource("data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "id", "type": "any"}, {"name": "name", "type": "any"}],
    }


def test_resource_validate_detector_infer_names():
    dialect = Dialect(header=False)
    detector = Detector(field_names=["id", "name"])
    resource = Resource("data/without-headers.csv", dialect=dialect, detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.fields[0].name == "id"
    assert resource.schema.fields[1].name == "name"
    assert resource.stats.rows == 3
    assert resource.labels == []
    assert resource.header == ["id", "name"]
