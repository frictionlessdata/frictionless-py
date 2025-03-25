import pathlib

import pytest

from frictionless import (
    Check,
    Checklist,
    Detector,
    Dialect,
    FrictionlessException,
    Resource,
    Schema,
    errors,
    platform,
)
from frictionless.resources import TableResource

# General


def test_resource_validate():
    resource = TableResource.from_descriptor({"name": "name", "path": "data/table.csv"})
    report = resource.validate()
    assert report.valid


def test_resource_validate_invalid_table():
    resource = TableResource.from_descriptor({"name": "name", "path": "data/invalid.csv"})
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


def test_resource_validate_resource_with_schema_as_string():
    resource = TableResource.from_descriptor(
        {"name": "name", "path": "data/table.csv", "schema": "data/schema.json"}
    )
    report = resource.validate()
    assert report.valid


def test_resource_validate_from_path():
    resource = TableResource(path="data/table.csv")
    report = resource.validate()
    assert report.valid


def test_resource_validate_invalid():
    resource = TableResource(path="data/invalid.csv")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


def test_resource_validate_blank_headers():
    resource = TableResource(path="data/blank-headers.csv")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 2, "blank-label"],
    ]


def test_resource_validate_duplicate_headers():
    resource = TableResource(path="data/duplicate-headers.csv")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "duplicate-label"],
        [None, 5, "duplicate-label"],
    ]


def test_resource_validate_defective_rows():
    resource = TableResource(path="data/defective-rows.csv")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 3, "missing-cell"],
        [3, 4, "extra-cell"],
    ]


def test_resource_validate_blank_rows():
    resource = TableResource(path="data/blank-rows.csv")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, None, "blank-row"],
    ]


def test_resource_validate_blank_rows_multiple():
    resource = TableResource(path="data/blank-rows-multiple.csv")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, None, "blank-row"],
        [5, None, "blank-row"],
        [6, None, "blank-row"],
        [7, None, "blank-row"],
        [8, None, "blank-row"],
        [9, None, "blank-row"],
        [10, None, "blank-row"],
        [11, None, "blank-row"],
        [12, None, "blank-row"],
        [13, None, "blank-row"],
        [14, None, "blank-row"],
    ]


def test_resource_validate_blank_cell_not_required():
    resource = TableResource(path="data/blank-cells.csv")
    report = resource.validate()
    assert report.valid


def test_resource_validate_no_data():
    resource = TableResource(path="data/empty.csv")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        ["source-error", "the source is empty"],
    ]


def test_resource_validate_no_rows():
    resource = TableResource(path="data/without-rows.csv")
    report = resource.validate()
    assert report.valid


def test_resource_validate_no_rows_with_compression():
    resource = TableResource(path="data/without-rows.csv.zip")
    report = resource.validate()
    assert report.valid


def test_resource_validate_source_invalid():
    # Reducing sample size to get raise on iter, not on open
    detector = Detector(sample_size=1)
    resource = TableResource(data=[["h"], [1], "bad"], detector=detector)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "source-error"],
    ]


def test_resource_validate_source_invalid_many_rows():
    # Reducing sample size to get raise on iter, not on open
    detector = Detector(sample_size=1)
    resource = TableResource(data=[["h"], [1], "bad", "bad"], detector=detector)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "source-error"],
    ]


def test_resource_validate_source_pathlib_path_table():
    resource = Resource(pathlib.Path("data/table.csv"))
    assert isinstance(resource, TableResource)
    report = resource.validate()
    assert report.valid


def test_resource_validate_pick_errors():
    resource = TableResource(path="data/invalid.csv")
    checklist = Checklist(pick_errors=["blank-label", "blank-row"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [4, None, "blank-row"],
    ]


def test_resource_validate_pick_errors_tags():
    resource = TableResource(path="data/invalid.csv")
    checklist = Checklist(pick_errors=["#header"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
    ]


def test_resource_validate_skip_errors():
    resource = TableResource(path="data/invalid.csv")
    checklist = Checklist(skip_errors=["blank-label", "blank-row"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [5, 5, "extra-cell"],
    ]


def test_resource_validate_skip_errors_tags():
    resource = TableResource(path="data/invalid.csv")
    checklist = Checklist(skip_errors=["#header"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


def test_resource_validate_invalid_limit_errors():
    resource = TableResource(path="data/invalid.csv")
    report = resource.validate(limit_errors=3)
    assert report.task.warnings == ["reached error limit: 3"]
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
    ]


def test_resource_validate_structure_errors_with_limit_errors():
    resource = TableResource(path="data/structure-errors.csv")
    report = resource.validate(limit_errors=3)
    assert report.task.warnings == ["reached error limit: 3"]
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, None, "blank-row"],
        [5, 4, "extra-cell"],
        [5, 5, "extra-cell"],
    ]


def test_resource_validate_custom_check():
    # Create check
    class custom(Check):
        def validate_row(self, row):
            yield errors.BlankRowError(
                note="",
                cells=list(map(str, row.values())),
                row_number=row.row_number,
            )

    # Validate resource
    resource = TableResource(path="data/table.csv")
    checklist = Checklist(checks=[custom()])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, None, "blank-row"],
        [3, None, "blank-row"],
    ]


def test_resource_validate_custom_check_with_arguments():
    # Create check
    class custom(Check):
        def __init__(self, *, row_number=None):
            self.row_number = row_number

        def validate_row(self, row):
            yield errors.BlankRowError(
                note="",
                cells=list(map(str, row.values())),
                row_number=self.row_number or row.row_number,
            )

    # Validate resource
    resource = TableResource(path="data/table.csv")
    checklist = Checklist(checks=[custom(row_number=1)])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [1, None, "blank-row"],
        [1, None, "blank-row"],
    ]


@pytest.mark.skip
def test_resource_validate_custom_check_bad_name():
    descriptor = {
        "path": "data/table.csv",
        "checklist": {
            "checks": [{"type": "bad"}],
        },
    }
    report = TableResource.from_descriptor(descriptor).validate()
    assert report.flatten(["type", "note"]) == [
        ["check-error", 'check type "bad" is not supported'],
    ]


# Bugs


def test_resource_validate_infer_fields_issue_223():
    source = [["name1", "name2"], ["123", "abc"], ["456", "def"], ["789", "ghi"]]
    detector = Detector(schema_patch={"fields": {"name": {"type": "string"}}})
    resource = TableResource(data=source, detector=detector)
    report = resource.validate()
    assert report.valid


def test_resource_validate_infer_fields_issue_225():
    source = [["name1", "name2"], ["123", None], ["456", None], ["789"]]
    detector = Detector(schema_patch={"fields": {"name": {"type": "string"}}})
    resource = TableResource(data=source, detector=detector)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "missing-cell"],
    ]


def test_resource_validate_fails_with_wrong_encoding_issue_274():
    # For now, by default encoding is detected incorrectly by chardet
    resource = TableResource(path="data/encoding-issue-274.csv", encoding="utf-8")
    report = resource.validate()
    assert report.valid


def test_resource_validate_wide_table_with_order_fields_issue_277():
    source = "data/issue-277.csv"
    schema = "data/issue-277.json"
    detector = Detector(schema_sync=True)
    resource = TableResource(path=source, schema=schema, detector=detector)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [49, 50, "constraint-error"],
        [68, 50, "constraint-error"],
        [69, 50, "constraint-error"],
    ]


@pytest.mark.skip
def test_validate_invalid_table_schema_issue_304():
    descriptor = {
        "data": [["name", "age"], ["Alex", "33"]],
        "schema": {
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "age", "type": "bad"},
            ]
        },
    }
    report = TableResource.from_descriptor(descriptor).validate()
    assert report.flatten(["type", "note"]) == [
        ["field-error", 'field type "bad" is not supported'],
    ]


def test_resource_validate_table_is_invalid_issue_312():
    resource = TableResource(path="data/issue-312.xlsx")
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [None, 5, "blank-label"],
        [5, None, "blank-row"],
    ]


def test_resource_validate_missing_local_file_raises_scheme_error_issue_315():
    resource = TableResource(path="bad-path.csv")
    report = resource.validate()
    assert report.stats["errors"] == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "scheme-error"
    assert note.count("[Errno 2]") and note.count("bad-path.csv")


def test_resource_validate_inline_not_a_binary_issue_349():
    with open("data/table.csv") as source:
        resource = TableResource(data=source, format="csv")
        report = resource.validate()
        assert report.valid


@pytest.mark.ci
def test_resource_validate_newline_inside_label_issue_811():
    detector = Detector(sample_size=8000)
    resource = TableResource(path="data/issue-811.csv", detector=detector)
    report = resource.validate()
    assert report.valid


def test_resource_validate_resource_from_json_format_issue_827():
    resource = TableResource(path="data/table.json")
    report = resource.validate()
    assert report.valid


def test_resource_validate_resource_none_is_not_iterable_enum_constraint_issue_833():
    resource = TableResource(path="data/issue-833.csv", schema="data/issue-833.json")
    report = resource.validate()
    assert report.valid


def test_resource_validate_resource_header_row_has_first_number_issue_870():
    resource = TableResource(path="data/issue-870.xlsx")
    report = resource.validate(limit_rows=5)
    assert report.valid


def test_validate_resource_duplicate_labels_with_sync_schema_issue_910():
    detector = Detector(schema_sync=True)
    report = TableResource(
        path="data/duplicate-column.csv",
        schema="data/duplicate-column-schema.json",
        detector=detector,
    ).validate()
    assert report.flatten(["type", "note"]) == [
        ["error", '"schema_sync" requires unique labels in the header'],
    ]


def test_resource_validate_resource_array_path_issue_991():
    with pytest.warns(UserWarning):
        resource = TableResource.from_descriptor("data/issue-991.resource.json")
        report = resource.validate()
        assert report.flatten(["type", "note"]) == [
            ["source-error", "the source is empty"],
        ]


def test_resource_validate_resource_metadata_errors_with_missing_values_993():
    with pytest.raises(FrictionlessException) as excinfo:
        TableResource.from_descriptor("data/resource-with-missingvalues-993.json")
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == '"missingValues" should be set as "schema.missingValues"'


@pytest.mark.skip
def test_resource_validate_resource_metadata_errors_with_fields_993():
    with pytest.raises(FrictionlessException) as excinfo:
        TableResource.from_descriptor("data/resource-with-fields-993.json")
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == '"fields" should be set as "schema.fields"'


# Checklist


def test_resource_validate_bound_checklist():
    checklist = Checklist(pick_errors=["blank-label", "blank-row"])
    resource = TableResource(path="data/invalid.csv")
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [4, None, "blank-row"],
    ]


# Compression


def test_resource_validate_compression():
    resource = TableResource(path="data/table.csv.zip")
    report = resource.validate()
    assert report.valid


def test_resource_validate_compression_explicit():
    resource = TableResource(path="data/table.csv.zip", compression="zip")
    report = resource.validate()
    assert report.valid


def test_resource_validate_compression_invalid():
    resource = TableResource(path="data/table.csv.zip", compression="bad")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        ["compression-error", 'compression "bad" is not supported'],
    ]


# Detector


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
    resource = TableResource(
        path="data/sync-schema.csv", schema=schema, detector=detector
    )
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
    resource = TableResource(data=source, schema=schema, detector=detector)
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
                {
                    "name": "language",
                    "type": "string",
                    "constraints": {"required": True},
                },
                {"name": "country", "type": "string"},
            ]
        }
    )
    detector = Detector(schema_sync=True)
    resource = TableResource(data=source, schema=schema, detector=detector)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [4, 4, "constraint-error", ["3", "Smith", "Paul", ""]],
    ]


def test_resource_validate_detector_patch_schema():
    detector = Detector(schema_patch={"missingValues": ["-"]})
    resource = TableResource(path="data/table.csv", detector=detector)
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
    resource = TableResource(path="data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
        ],
        "missingValues": ["-"],
    }


def test_resource_validate_detector_infer_type_string():
    detector = Detector(field_type="string")
    resource = TableResource(path="data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
        ],
    }


def test_resource_validate_detector_infer_type_any():
    detector = Detector(field_type="any")
    resource = TableResource(path="data/table.csv", detector=detector)
    report = resource.validate()
    assert report.valid
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "id", "type": "any"}, {"name": "name", "type": "any"}],
    }


def test_resource_validate_detector_infer_names():
    dialect = Dialect(header=False)
    detector = Detector(field_names=["id", "name"])
    resource = TableResource(
        path="data/without-headers.csv", dialect=dialect, detector=detector
    )
    report = resource.validate()
    assert report.valid
    assert resource.schema.fields[0].name == "id"
    assert resource.schema.fields[1].name == "name"
    assert resource.stats.rows == 3
    assert resource.labels == []
    assert resource.header == ["id", "name"]


# Encoding


def test_resource_validate_encoding():
    resource = TableResource(path="data/table.csv", encoding="utf-8")
    report = resource.validate()
    assert report.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_validate_encoding_invalid():
    resource = TableResource(path="data/latin1.csv", encoding="utf-8")
    report = resource.validate()
    assert not report.valid
    assert report.flatten(["type", "note"]) == [
        [
            "encoding-error",
            "'utf-8' codec can't decode byte 0xa9 in position 20: invalid start byte",
        ],
    ]


# File


def test_resource_validate_format_non_tabular():
    resource = Resource("data/table.bad")
    report = resource.validate()
    assert report.valid


def test_resource_validate_invalid_resource_standards_v2_strict():
    report = Resource.validate_descriptor({"path": "data/table.csv"})
    assert report.flatten(["type", "note"]) == [
        ["resource-error", "'name' is a required property"],
    ]


# Format


def test_resource_validate_format():
    resource = TableResource(path="data/table.csv", format="csv")
    report = resource.validate()
    assert report.valid


# Stats


def test_resource_validate_stats_hash():
    hash = "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    resource = TableResource(path="data/table.csv", hash=hash)
    report = resource.validate()
    assert report.task.valid


def test_resource_validate_stats_hash_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    resource = TableResource(path="data/table.csv", hash="bad")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        [
            "hash-count",
            'expected is "bad" and actual is "%s"' % hash,
        ],
    ]


def test_resource_validate_stats_bytes():
    resource = TableResource(path="data/table.csv", bytes=30)
    report = resource.validate()
    assert report.task.valid


def test_resource_validate_stats_bytes_invalid():
    resource = TableResource(path="data/table.csv", bytes=40)
    report = resource.validate()
    assert report.task.error.to_descriptor().get("rowNumber") is None
    assert report.task.error.to_descriptor().get("fieldNumber") is None
    assert report.flatten(["type", "note"]) == [
        ["byte-count", 'expected is "40" and actual is "30"'],
    ]


def test_resource_validate_stats_rows():
    resource = TableResource(path="data/table.csv", rows=2)
    report = resource.validate()
    assert report.task.valid


def test_resource_validate_stats_rows_invalid():
    resource = TableResource(path="data/table.csv", rows=3)
    report = resource.validate()
    assert report.task.error.to_descriptor().get("rowNumber") is None
    assert report.task.error.to_descriptor().get("fieldNumber") is None
    assert report.flatten(["type", "note"]) == [
        ["row-count", 'expected is "3" and actual is "2"'],
    ]


def test_resource_validate_stats_not_supported_hash_algorithm():
    resource = TableResource.from_descriptor(
        {
            "name": "name",
            "path": "data/table.csv",
            "hash": "sha1:db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e",
        }
    )
    report = resource.validate()
    assert report.task.warnings == ["hash is ignored; supported algorithms: md5/sha256"]


# Scheme


def test_resource_validate_scheme():
    resource = TableResource(path="data/table.csv", scheme="file")
    report = resource.validate()
    assert report.valid


def test_resource_validate_scheme_invalid():
    resource = TableResource(path="bad://data/table.csv")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        ["scheme-error", 'scheme "bad" is not supported'],
    ]
