import pytest
import pathlib
from frictionless import Schema, Detector, Dialect, Check, Stats
from frictionless import validate, formats, errors, platform, system


# General


def test_validate():
    report = validate({"path": "data/table.csv"})
    assert report.valid


def test_validate_invalid_source():
    report = validate("bad.json", type="resource")
    assert report.stats.errors == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "resource-error"
    assert note.count("[Errno 2]") and note.count("bad.json")


def test_validate_invalid_resource():
    report = validate({"path": "data/table.csv", "schema": "bad"})
    assert report.stats.errors == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "schema-error"
    assert note.count("[Errno 2]") and note.count("bad")


def test_validate_forbidden_value_task_error():
    descriptor = {
        "path": "data/table.csv",
        "checklist": {
            "checks": [
                {"type": "forbidden-value", "fieldName": "bad", "forbidden": [2]},
            ]
        },
    }
    report = validate(descriptor)
    assert report.flatten(["type", "note"]) == [
        ["check-error", "'values' is a required property"],
    ]


def test_validate_invalid_resource_standards_v2_strict():
    with system.use_context(standards="v2-strict"):
        report = validate({"path": "data/table.csv"})
    assert report.flatten(["type", "note"]) == [
        ["resource-error", 'property "name" is required by standards "v2-strict"'],
        ["resource-error", 'property "type" is required by standards "v2-strict"'],
        ["resource-error", 'property "scheme" is required by standards "v2-strict"'],
        ["resource-error", 'property "format" is required by standards "v2-strict"'],
        ["resource-error", 'property "encoding" is required by standards "v2-strict"'],
        ["resource-error", 'property "mediatype" is required by standards "v2-strict"'],
    ]


def test_validate_invalid_table():
    report = validate({"path": "data/invalid.csv"})
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


def test_validate_resource_with_schema_as_string():
    report = validate({"path": "data/table.csv", "schema": "data/schema.json"})
    assert report.valid


def test_validate_from_path():
    report = validate("data/table.csv")
    assert report.valid


def test_validate_invalid():
    report = validate("data/invalid.csv")
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


def test_validate_blank_headers():
    report = validate("data/blank-headers.csv")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 2, "blank-label"],
    ]


def test_validate_duplicate_headers():
    report = validate("data/duplicate-headers.csv")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "duplicate-label"],
        [None, 5, "duplicate-label"],
    ]


def test_validate_defective_rows():
    report = validate("data/defective-rows.csv")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 3, "missing-cell"],
        [3, 4, "extra-cell"],
    ]


def test_validate_blank_rows():
    report = validate("data/blank-rows.csv")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, None, "blank-row"],
    ]


def test_validate_blank_rows_multiple():
    report = validate("data/blank-rows-multiple.csv")
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


def test_validate_blank_cell_not_required():
    report = validate("data/blank-cells.csv")
    assert report.valid


def test_validate_no_data():
    report = validate("data/empty.csv")
    assert report.flatten(["type", "note"]) == [
        ["source-error", "the source is empty"],
    ]


def test_validate_no_rows():
    report = validate("data/without-rows.csv")
    assert report.valid


def test_validate_no_rows_with_compression():
    report = validate("data/without-rows.csv.zip")
    assert report.valid


def test_validate_source_invalid():
    # Reducing sample size to get raise on iter, not on open
    detector = Detector(sample_size=1)
    report = validate([["h"], [1], "bad"], detector=detector)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "source-error"],
    ]


def test_validate_source_pathlib_path_table():
    report = validate(pathlib.Path("data/table.csv"))
    assert report.valid


# Scheme


def test_validate_scheme():
    report = validate("data/table.csv", scheme="file")
    assert report.valid


def test_validate_scheme_invalid():
    report = validate("bad://data/table.csv")
    assert report.flatten(["type", "note"]) == [
        ["scheme-error", 'scheme "bad" is not supported'],
    ]


# Format


def test_validate_format():
    report = validate("data/table.csv", format="csv")
    assert report.valid


def test_validate_format_non_tabular():
    report = validate("data/table.bad")
    assert report.valid


# Encoding


def test_validate_encoding():
    report = validate("data/table.csv", encoding="utf-8")
    assert report.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_encoding_invalid():
    report = validate("data/latin1.csv", encoding="utf-8")
    assert not report.valid
    assert report.flatten(["type", "note"]) == [
        [
            "encoding-error",
            "'utf-8' codec can't decode byte 0xa9 in position 20: invalid start byte",
        ],
    ]


# Compression


def test_validate_compression():
    report = validate("data/table.csv.zip")
    assert report.valid


def test_validate_compression_explicit():
    report = validate("data/table.csv.zip", compression="zip")
    assert report.valid


def test_validate_compression_invalid():
    report = validate("data/table.csv.zip", compression="bad")
    assert report.flatten(["type", "note"]) == [
        ["compression-error", 'compression "bad" is not supported'],
    ]


# Dialect


def test_validate_layout_none():
    dialect = Dialect(header=False)
    report = validate("data/without-headers.csv", dialect=dialect)
    assert report.valid
    assert report.task.stats.rows == 3


def test_validate_layout_none_extra_cell():
    dialect = Dialect(header=False)
    report = validate("data/without-headers-extra.csv", dialect=dialect)
    assert report.task.stats.rows == 3
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, 3, "extra-cell"],
    ]


def test_validate_layout_number():
    dialect = Dialect(header_rows=[2])
    report = validate("data/matrix.csv", dialect=dialect)
    assert report.task.stats.rows == 3
    assert report.valid


def test_validate_layout_list_of_numbers():
    dialect = Dialect(header_rows=[2, 3, 4])
    report = validate("data/matrix.csv", dialect=dialect)
    assert report.task.stats.rows == 1
    assert report.valid


def test_validate_layout_list_of_numbers_and_headers_join():
    dialect = Dialect(header_rows=[2, 3, 4], header_join=".")
    report = validate("data/matrix.csv", dialect=dialect)
    assert report.task.stats.rows == 1
    assert report.valid


def test_validate_layout_skip_rows():
    dialect = Dialect(comment_char="41", comment_rows=[2])
    report = validate("data/matrix.csv", dialect=dialect)
    assert report.task.stats.rows == 2
    assert report.task.valid


def test_validate_dialect_delimiter():
    control = formats.CsvControl(delimiter=";")
    report = validate("data/delimiter.csv", control=control)
    assert report.valid
    assert report.task.stats.rows == 2


# Schema


def test_validate_schema_invalid_json():
    report = validate("data/table.csv", schema="data/invalid.json")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "schema-error"],
    ]


def test_validate_schema_extra_headers_and_cells():
    schema = Schema.from_descriptor({"fields": [{"name": "id", "type": "integer"}]})
    report = validate("data/table.csv", schema=schema)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 2, "extra-label"],
        [2, 2, "extra-cell"],
        [3, 2, "extra-cell"],
    ]


def test_validate_schema_multiple_errors():
    source = "data/schema-errors.csv"
    schema = "data/schema-valid.json"
    report = validate(source, schema=schema, pick_errors=["#row"], limit_errors=3)
    assert report.task.warnings == ["reached error limit: 3"]
    assert report.task.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 1, "type-error"],
        [4, 2, "constraint-error"],
        [4, 3, "constraint-error"],
    ]


def test_validate_schema_min_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "word", "type": "string", "constraints": {"minLength": 2}},
            ]
        }
    )
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 2, "constraint-error"],
    ]


def test_validate_schema_max_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "word", "type": "string", "constraints": {"maxLength": 2}},
            ]
        }
    )
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_validate_schema_minimum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "score", "type": "integer", "constraints": {"minimum": 2}},
            ]
        }
    )
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 2, "constraint-error"],
    ]


def test_validate_schema_maximum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "score", "type": "integer", "constraints": {"maximum": 2}},
            ]
        }
    )
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_validate_schema_foreign_key_error_self_referencing():
    source = {
        "path": "data/nested.csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "cat", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "foreignKeys": [
                {"fields": "cat", "reference": {"resource": "", "fields": "id"}}
            ],
        },
    }
    report = validate(source)
    assert report.valid


def test_validate_schema_foreign_key_error_self_referencing_invalid():
    source = {
        "path": "data/nested-invalid.csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "cat", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "foreignKeys": [
                {"fields": "cat", "reference": {"resource": "", "fields": "id"}}
            ],
        },
    }
    report = validate(source)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [6, None, "foreign-key", ["5", "6", "Rome"]],
    ]


def test_validate_schema_unique_error():
    report = validate(
        "data/unique-field.csv",
        schema="data/unique-field.json",
        pick_errors=["unique-error"],
    )
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [10, 1, "unique-error"],
    ]


def test_validate_schema_unique_error_and_type_error():
    source = [
        ["id", "unique_number"],
        ["a1", 100],
        ["a2", "bad"],
        ["a3", 100],
        ["a4", 0],
        ["a5", 0],
    ]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {
                    "name": "id",
                    "type": "string",
                },
                {
                    "name": "unique_number",
                    "type": "number",
                    "constraints": {"unique": True},
                },
            ]
        }
    )
    report = validate(source, schema=schema)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [3, 2, "type-error", ["a2", "bad"]],
        [4, 2, "unique-error", ["a3", "100"]],
        [6, 2, "unique-error", ["a5", "0"]],
    ]


def test_validate_schema_primary_key_error():
    report = validate(
        "data/unique-field.csv",
        schema="data/unique-field.json",
        pick_errors=["primary-key"],
    )
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [10, None, "primary-key"],
    ]


def test_validate_schema_primary_key_and_unique_error():
    report = validate(
        "data/unique-field.csv",
        schema="data/unique-field.json",
    )
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [10, 1, "unique-error"],
        [10, None, "primary-key"],
    ]


def test_validate_schema_primary_key_error_composite():
    source = [
        ["id", "name"],
        [1, "Alex"],
        [1, "John"],
        ["", "Paul"],
        [1, "John"],
        ["", None],
    ]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "primaryKey": ["id", "name"],
        }
    )
    report = validate(source, schema=schema)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [5, None, "primary-key"],
        [6, None, "blank-row"],
        [6, None, "primary-key"],
    ]


# Stats


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_stats_hash():
    sha256 = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", stats=Stats(sha256=sha256))
    assert report.task.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_stats_hash_invalid():
    sha256 = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", stats=Stats(sha256="bad"))
    assert report.flatten(["type", "note"]) == [
        [
            "sha256-count",
            'expected is "bad" and actual is "%s"' % sha256,
        ],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_stats_bytes():
    report = validate("data/table.csv", stats=Stats(bytes=30))
    assert report.task.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_stats_bytes_invalid():
    report = validate("data/table.csv", stats=Stats(bytes=40))
    assert report.task.error.to_descriptor().get("rowNumber") is None
    assert report.task.error.to_descriptor().get("fieldNumber") is None
    assert report.flatten(["type", "note"]) == [
        ["byte-count", 'expected is "40" and actual is "30"'],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_stats_rows():
    report = validate("data/table.csv", stats=Stats(rows=2))
    assert report.task.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_stats_rows_invalid():
    report = validate("data/table.csv", stats=Stats(rows=3))
    assert report.task.error.to_descriptor().get("rowNumber") is None
    assert report.task.error.to_descriptor().get("fieldNumber") is None
    assert report.flatten(["type", "note"]) == [
        ["row-count", 'expected is "3" and actual is "2"'],
    ]


# Detector


def test_validate_detector_sync_schema():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
        }
    )
    detector = Detector(schema_sync=True)
    report = validate("data/sync-schema.csv", schema=schema, detector=detector)
    assert report.task.stats.fields == 2
    assert report.valid


def test_validate_detector_sync_schema_invalid():
    source = [["LastName", "FirstName", "Address"], ["Test", "Tester", "23 Avenue"]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "FirstName", "type": "string"},
                {"name": "LastName", "type": "string"},
            ]
        }
    )
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
    report = validate(source, schema=schema, detector=detector)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [4, 4, "constraint-error", ["3", "Smith", "Paul", ""]],
    ]


def test_validate_detector_patch_schema():
    detector = Detector(schema_patch={"missingValues": ["-"]})
    report = validate("data/table.csv", detector=detector)
    assert report.task.stats.fields == 2
    assert report.valid


def test_validate_detector_patch_schema_fields():
    detector = Detector(
        schema_patch={"fields": {"id": {"type": "string"}}, "missingValues": ["-"]}
    )
    report = validate("data/table.csv", detector=detector)
    assert report.task.stats.fields == 2
    assert report.valid


def test_validate_detector_infer_type_string():
    detector = Detector(field_type="string")
    report = validate("data/table.csv", detector=detector)
    assert report.task.stats.fields == 2
    assert report.valid


def test_validate_detector_infer_type_any():
    detector = Detector(field_type="any")
    report = validate("data/table.csv", detector=detector)
    assert report.task.stats.fields == 2
    assert report.valid


def test_validate_detector_infer_names():
    dialect = Dialect(header=False)
    detector = Detector(field_names=["id", "name"])
    report = validate("data/without-headers.csv", dialect=dialect, detector=detector)
    assert report.task.stats.fields == 2
    assert report.task.stats.rows == 3
    assert report.valid


# Validation


def test_validate_pick_errors():
    report = validate("data/invalid.csv", pick_errors=["blank-label", "blank-row"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [4, None, "blank-row"],
    ]


def test_validate_pick_errors_tags():
    report = validate("data/invalid.csv", pick_errors=["#header"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
    ]


def test_validate_skip_errors():
    report = validate("data/invalid.csv", skip_errors=["blank-label", "blank-row"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [5, 5, "extra-cell"],
    ]


def test_validate_skip_errors_tags():
    report = validate("data/invalid.csv", skip_errors=["#header"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


def test_validate_invalid_limit_errors():
    report = validate("data/invalid.csv", limit_errors=3)
    assert report.task.warnings == ["reached error limit: 3"]
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
    ]


def test_validate_structure_errors_with_limit_errors():
    report = validate("data/structure-errors.csv", limit_errors=3)
    assert report.task.warnings == ["reached error limit: 3"]
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, None, "blank-row"],
        [5, 4, "extra-cell"],
        [5, 5, "extra-cell"],
    ]


def test_validate_custom_check():

    # Create check
    class custom(Check):
        def validate_row(self, row):
            yield errors.BlankRowError(
                note="",
                cells=list(map(str, row.values())),
                row_number=row.row_number,
            )

    # Validate resource
    report = validate("data/table.csv", checks=[custom()])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, None, "blank-row"],
        [3, None, "blank-row"],
    ]


def test_validate_custom_check_with_arguments():

    # Create check
    class custom(Check):
        def __init__(self, row_number=None):
            self.row_number = row_number

        def validate_row(self, row):
            yield errors.BlankRowError(
                note="",
                cells=list(map(str, row.values())),
                row_number=self.row_number or row.row_number,
            )

    # Validate resource
    report = validate("data/table.csv", checks=[custom(row_number=1)])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [1, None, "blank-row"],
        [1, None, "blank-row"],
    ]


def test_validate_custom_check_bad_name():
    descriptor = {
        "path": "data/table.csv",
        "checklist": {
            "checks": [{"type": "bad"}],
        },
    }
    report = validate(descriptor)
    assert report.flatten(["type", "note"]) == [
        ["check-error", 'check type "bad" is not supported'],
    ]


# Bugs


def test_validate_infer_fields_issue_223():
    source = [["name1", "name2"], ["123", "abc"], ["456", "def"], ["789", "ghi"]]
    detector = Detector(schema_patch={"fields": {"name": {"type": "string"}}})
    report = validate(source, detector=detector)
    assert report.valid


def test_validate_infer_fields_issue_225():
    source = [["name1", "name2"], ["123", None], ["456", None], ["789"]]
    detector = Detector(schema_patch={"fields": {"name": {"type": "string"}}})
    report = validate(source, detector=detector)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "missing-cell"],
    ]


def test_validate_fails_with_wrong_encoding_issue_274():
    # For now, by default encoding is detected incorectly by chardet
    report = validate("data/encoding-issue-274.csv", encoding="utf-8")
    assert report.valid


def test_validate_wide_table_with_order_fields_issue_277():
    source = "data/issue-277.csv"
    schema = "data/issue-277.json"
    detector = Detector(schema_sync=True)
    report = validate(source, schema=schema, detector=detector)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [49, 50, "constraint-error"],
        [68, 50, "constraint-error"],
        [69, 50, "constraint-error"],
    ]


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
    report = validate(descriptor)
    assert report.flatten(["type", "note"]) == [
        ["field-error", 'field type "bad" is not supported'],
    ]


def test_validate_table_is_invalid_issue_312():
    report = validate("data/issue-312.xlsx")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [None, 5, "blank-label"],
        [5, None, "blank-row"],
    ]


def test_validate_missing_local_file_raises_scheme_error_issue_315():
    report = validate("bad-path.csv")
    assert report.stats.errors == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "scheme-error"
    assert note.count("[Errno 2]") and note.count("bad-path.csv")


def test_validate_inline_not_a_binary_issue_349():
    with open("data/table.csv") as source:
        report = validate(source)
        assert report.valid


@pytest.mark.ci
def test_validate_newline_inside_label_issue_811():
    detector = Detector(sample_size=8000)
    report = validate("data/issue-811.csv", detector=detector)
    assert report.valid


def test_validate_resource_from_json_format_issue_827():
    report = validate(path="data/table.json")
    assert report.valid


def test_validate_resource_none_is_not_iterable_enum_constraint_issue_833():
    report = validate("data/issue-833.csv", schema="data/issue-833.json")
    assert report.valid


def test_validate_resource_header_row_has_first_number_issue_870():
    report = validate("data/issue-870.xlsx", limit_rows=5)
    assert report.valid


def test_validate_resource_array_path_issue_991():
    with pytest.warns(UserWarning):
        report = validate("data/issue-991.resource.json")
        assert report.flatten(["type", "note"]) == [
            ["source-error", "the source is empty"],
        ]


def test_validate_resource_duplicate_labels_with_sync_schema_issue_910():
    detector = Detector(schema_sync=True)
    report = validate(
        "data/duplicate-column.csv",
        schema="data/duplicate-column-schema.json",
        detector=detector,
    )
    assert report.flatten(["type", "note"]) == [
        ["error", '"schema_sync" requires unique labels in the header'],
    ]
