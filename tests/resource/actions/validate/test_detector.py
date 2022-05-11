from frictionless import Detector, validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_detector_sync_schema():
    schema = {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }
    detector = Detector(schema_sync=True)
    report = validate("data/sync-schema.csv", schema=schema, detector=detector)
    assert report.valid
    assert report.task.resource.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "id", "type": "integer"},
        ],
    }


def test_validate_detector_sync_schema_invalid():
    source = [["LastName", "FirstName", "Address"], ["Test", "Tester", "23 Avenue"]]
    schema = {"fields": [{"name": "id"}, {"name": "FirstName"}, {"name": "LastName"}]}
    detector = Detector(schema_sync=True)
    report = validate(source, schema=schema, detector=detector)
    assert report.valid


def test_validate_detector_headers_errors():
    source = [
        ["id", "last_name", "first_name", "language"],
        [1, "Alex", "John", "English"],
        [2, "Peters", "John", "Afrikaans"],
        [3, "Smith", "Paul", None],
    ]
    schema = {
        "fields": [
            {"name": "id", "type": "number"},
            {"name": "language", "constraints": {"required": True}},
            {"name": "country"},
        ]
    }
    detector = Detector(schema_sync=True)
    report = validate(source, schema=schema, detector=detector)
    assert report.flatten(["rowPosition", "fieldPosition", "code", "cells"]) == [
        [4, 4, "constraint-error", ["3", "Smith", "Paul", ""]],
    ]


def test_validate_detector_patch_schema():
    detector = Detector(schema_patch={"missingValues": ["-"]})
    report = validate("data/table.csv", detector=detector)
    assert report.valid
    assert report.task.resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "missingValues": ["-"],
    }


def test_validate_detector_patch_schema_fields():
    detector = Detector(
        schema_patch={"fields": {"id": {"type": "string"}}, "missingValues": ["-"]}
    )
    report = validate("data/table.csv", detector=detector)
    assert report.valid
    assert report.task.resource.schema == {
        "fields": [{"name": "id", "type": "string"}, {"name": "name", "type": "string"}],
        "missingValues": ["-"],
    }


def test_validate_detector_infer_type_string():
    detector = Detector(field_type="string")
    report = validate("data/table.csv", detector=detector)
    assert report.valid
    assert report.task.resource.schema == {
        "fields": [{"name": "id", "type": "string"}, {"name": "name", "type": "string"}],
    }


def test_validate_detector_infer_type_any():
    detector = Detector(field_type="any")
    report = validate("data/table.csv", detector=detector)
    assert report.valid
    assert report.task.resource.schema == {
        "fields": [{"name": "id", "type": "any"}, {"name": "name", "type": "any"}],
    }


def test_validate_detector_infer_names():
    detector = Detector(field_names=["id", "name"])
    report = validate(
        "data/without-headers.csv",
        layout={"header": False},
        detector=detector,
    )
    assert report.task.resource.schema["fields"][0]["name"] == "id"
    assert report.task.resource.schema["fields"][1]["name"] == "name"
    assert report.task.resource.stats["rows"] == 3
    assert report.task.resource.labels == []
    assert report.task.resource.header == ["id", "name"]
    assert report.valid
