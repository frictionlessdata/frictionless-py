import pytest
import pathlib
from frictionless import validate, Detector, Layout, Check, errors, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


def test_validate():
    report = validate({"path": "data/table.csv"})
    assert report.valid


def test_validate_invalid_source():
    report = validate("bad.json", type="resource")
    assert report.flatten(["code", "note"]) == [
        [
            "resource-error",
            'cannot extract metadata "bad.json" because "[Errno 2] No such file or directory: \'bad.json\'"',
        ]
    ]


def test_validate_invalid_resource():
    report = validate({"path": "data/table.csv", "schema": "bad"})
    assert report.flatten(["code", "note"]) == [
        [
            "schema-error",
            'cannot extract metadata "bad" because "[Errno 2] No such file or directory: \'bad\'"',
        ]
    ]


def test_validate_invalid_resource_original():
    report = validate({"path": "data/table.csv"}, original=True)
    assert report.flatten(["code", "note"]) == [
        [
            "resource-error",
            '"{\'path\': \'data/table.csv\'} is not valid under any of the given schemas" at "" in metadata and at "oneOf" in profile',
        ]
    ]


def test_validate_invalid_table():
    report = validate({"path": "data/invalid.csv"})
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 2, "blank-label"],
    ]


def test_validate_duplicate_headers():
    report = validate("data/duplicate-headers.csv")
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "duplicate-label"],
        [None, 5, "duplicate-label"],
    ]


def test_validate_defective_rows():
    report = validate("data/defective-rows.csv")
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 3, "missing-cell"],
        [3, 4, "extra-cell"],
    ]


def test_validate_blank_rows():
    report = validate("data/blank-rows.csv")
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "blank-row"],
    ]


def test_validate_blank_rows_multiple():
    report = validate("data/blank-rows-multiple.csv")
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    assert report.flatten(["code", "note"]) == [
        ["source-error", "the source is empty"],
    ]


def test_validate_no_rows():
    report = validate("data/without-rows.csv")
    assert report.valid


def test_validate_no_rows_with_compression():
    report = validate("data/without-rows.csv.zip")
    assert report.valid


def test_validate_task_error():
    report = validate("data/table.csv", limit_rows="bad")
    assert report.flatten(["code"]) == [
        ["task-error"],
    ]


def test_validate_source_invalid():
    # Reducing sample size to get raise on iter, not on open
    detector = Detector(sample_size=1)
    report = validate([["h"], [1], "bad"], detector=detector)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    assert report.flatten(["code", "note"]) == [
        ["scheme-error", 'cannot create loader "bad". Try installing "frictionless-bad"'],
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


def test_validate_encoding_invalid():
    report = validate("data/latin1.csv", encoding="utf-8")
    assert not report.valid
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
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
    assert report.flatten(["code", "note"]) == [
        ["compression-error", 'compression "bad" is not supported'],
    ]


# Dialect


def test_validate_dialect_delimiter():
    report = validate("data/delimiter.csv", dialect={"delimiter": ";"})
    assert report.valid
    assert report.task.resource.stats["rows"] == 2


# Layout


def test_validate_layout_none():
    layout = Layout(header=False)
    report = validate("data/without-headers.csv", layout=layout)
    assert report.valid
    assert report.task.resource.stats["rows"] == 3
    assert report.task.resource.layout.header is False
    assert report.task.resource.labels == []
    assert report.task.resource.header == ["field1", "field2"]


def test_validate_layout_none_extra_cell():
    layout = Layout(header=False)
    report = validate("data/without-headers-extra.csv", layout=layout)
    assert report.task.resource.stats["rows"] == 3
    assert report.task.resource.layout.header is False
    assert report.task.resource.labels == []
    assert report.task.resource.header == ["field1", "field2"]
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 3, "extra-cell"],
    ]


def test_validate_layout_number():
    layout = Layout(header_rows=[2])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["11", "12", "13", "14"]
    assert report.valid


def test_validate_layout_list_of_numbers():
    layout = Layout(header_rows=[2, 3, 4])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["11 21 31", "12 22 32", "13 23 33", "14 24 34"]
    assert report.valid


def test_validate_layout_list_of_numbers_and_headers_join():
    layout = Layout(header_rows=[2, 3, 4], header_join=".")
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["11.21.31", "12.22.32", "13.23.33", "14.24.34"]
    assert report.valid


def test_validate_layout_pick_fields():
    layout = Layout(pick_fields=[2, "f3"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_pick_fields_regex():
    layout = Layout(pick_fields=["<regex>f[23]"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_skip_fields():
    layout = Layout(skip_fields=[1, "f4"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_skip_fields_regex():
    layout = Layout(skip_fields=["<regex>f[14]"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_limit_fields():
    layout = Layout(limit_fields=1)
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_offset_fields():
    layout = Layout(offset_fields=3)
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f4"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_limit_and_offset_fields():
    layout = Layout(limit_fields=2, offset_fields=1)
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_pick_rows():
    layout = Layout(pick_rows=[1, 3, "31"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_pick_rows_regex():
    layout = Layout(pick_rows=["<regex>[f23]1"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows():
    layout = Layout(skip_rows=[2, "41"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows_regex():
    layout = Layout(skip_rows=["<regex>[14]1"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows_blank():
    layout = Layout(skip_rows=["<blank>"])
    report = validate("data/blank-rows.csv", layout=layout)
    assert report.task.resource.header == ["id", "name", "age"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_pick_rows_and_fields():
    layout = Layout(pick_rows=[1, 3, "31"], pick_fields=[2, "f3"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows_and_fields():
    layout = Layout(skip_rows=[2, "41"], skip_fields=[1, "f4"])
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_limit_rows():
    layout = Layout(limit_rows=1)
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 1
    assert report.task.valid


def test_validate_layout_offset_rows():
    layout = Layout(offset_rows=3)
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 1
    assert report.task.valid


def test_validate_layout_limit_and_offset_rows():
    layout = Layout(limit_rows=2, offset_rows=1)
    report = validate("data/matrix.csv", layout=layout)
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_invalid_limit_rows():
    layout = Layout(limit_rows=2)
    report = validate("data/invalid.csv", layout=layout)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
    ]


def test_validate_layout_structure_errors_with_limit_rows():
    layout = Layout(limit_rows=3)
    report = validate("data/structure-errors.csv", layout=layout)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "blank-row"],
    ]


# Schema


def test_validate_schema_invalid():
    source = [["name", "age"], ["Alex", "33"]]
    schema = {"fields": [{"name": "name"}, {"name": "age", "type": "bad"}]}
    report = validate(source, schema=schema)
    assert report.flatten(["code", "note"]) == [
        [
            "field-error",
            "\"{'name': 'age', 'type': 'bad'} is not valid under any of the given schemas\" at \"\" in metadata and at \"anyOf\" in profile",
        ],
    ]


def test_validate_schema_invalid_json():
    report = validate("data/table.csv", schema="data/invalid.json")
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "schema-error"],
    ]


def test_validate_schema_extra_headers_and_cells():
    schema = {"fields": [{"name": "id", "type": "integer"}]}
    report = validate("data/table.csv", schema=schema)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 2, "extra-label"],
        [2, 2, "extra-cell"],
        [3, 2, "extra-cell"],
    ]


def test_validate_schema_multiple_errors():
    source = "data/schema-errors.csv"
    schema = "data/schema-valid.json"
    report = validate(source, schema=schema, pick_errors=["#row"], limit_errors=3)
    assert report.task.partial
    assert report.task.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 1, "type-error"],
        [4, 2, "constraint-error"],
        [4, 3, "constraint-error"],
    ]


def test_validate_schema_min_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "word", "type": "string", "constraints": {"minLength": 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 2, "constraint-error"],
    ]


def test_validate_schema_max_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "word", "type": "string", "constraints": {"maxLength": 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_validate_schema_minimum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "score", "type": "integer", "constraints": {"minimum": 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 2, "constraint-error"],
    ]


def test_validate_schema_maximum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "score", "type": "integer", "constraints": {"maximum": 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [6, None, "foreign-key-error"],
    ]


def test_validate_schema_unique_error():
    report = validate(
        "data/unique-field.csv",
        schema="data/unique-field.json",
        pick_errors=["unique-error"],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [10, 1, "unique-error"],
    ]


def test_validate_schema_unique_error_and_type_error():
    source = [
        ["id", "unique_number"],
        ["a1", 100],
        ["a2", "bad"],
        ["a3", 100],
    ]
    schema = {
        "fields": [
            {"name": "id"},
            {"name": "unique_number", "type": "number", "constraints": {"unique": True}},
        ]
    }
    report = validate(source, schema=schema)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 2, "type-error"],
        [4, 2, "unique-error"],
    ]


def test_validate_schema_primary_key_error():
    report = validate(
        "data/unique-field.csv",
        schema="data/unique-field.json",
        pick_errors=["primary-key-error"],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [10, None, "primary-key-error"],
    ]


def test_validate_schema_primary_key_and_unique_error():
    report = validate(
        "data/unique-field.csv",
        schema="data/unique-field.json",
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [10, 1, "unique-error"],
        [10, None, "primary-key-error"],
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
    schema = {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "primaryKey": ["id", "name"],
    }
    report = validate(source, schema=schema)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [5, None, "primary-key-error"],
        [6, None, "blank-row"],
        [6, None, "primary-key-error"],
    ]


# Stats


def test_validate_stats_hash():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["hash-count-error", 'expected md5 is "bad" and actual is "%s"' % hash],
        ]


def test_validate_stats_hash_md5():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_md5_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["hash-count-error", 'expected md5 is "bad" and actual is "%s"' % hash],
        ]


def test_validate_stats_hash_sha1():
    hash = "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"
    report = validate("data/table.csv", hashing="sha1", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_sha1_invalid():
    hash = "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"
    report = validate("data/table.csv", hashing="sha1", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["hash-count-error", 'expected sha1 is "bad" and actual is "%s"' % hash],
        ]


def test_validate_stats_hash_sha256():
    hash = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", hashing="sha256", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_sha256_invalid():
    hash = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", hashing="sha256", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            [
                "hash-count-error",
                'expected sha256 is "bad" and actual is "%s"' % hash,
            ],
        ]


def test_validate_stats_hash_sha512():
    hash = "d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd"
    report = validate("data/table.csv", hashing="sha512", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_sha512_invalid():
    hash = "d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd"
    report = validate("data/table.csv", hashing="sha512", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            [
                "hash-count-error",
                'expected sha512 is "bad" and actual is "%s"' % hash,
            ],
        ]


def test_validate_stats_bytes():
    report = validate("data/table.csv", stats={"bytes": 30})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_bytes_invalid():
    report = validate("data/table.csv", stats={"bytes": 40})
    assert report.task.error.get("rowPosition") is None
    assert report.task.error.get("fieldPosition") is None
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["byte-count-error", 'expected is "40" and actual is "30"'],
        ]


def test_validate_stats_rows():
    report = validate("data/table.csv", stats={"rows": 2})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_rows_invalid():
    report = validate("data/table.csv", stats={"rows": 3})
    assert report.task.error.get("rowPosition") is None
    assert report.task.error.get("fieldPosition") is None
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["row-count-error", 'expected is "3" and actual is "2"'],
        ]


# Detector


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
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 4, "constraint-error"],
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


# Validation


def test_validate_pick_errors():
    report = validate("data/invalid.csv", pick_errors=["blank-label", "blank-row"])
    assert report.task.scope == ["blank-label", "blank-row"]
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [4, None, "blank-row"],
    ]


def test_validate_pick_errors_tags():
    report = validate("data/invalid.csv", pick_errors=["#header"])
    assert report.task.scope == [
        "blank-header",
        "extra-label",
        "missing-label",
        "blank-label",
        "duplicate-label",
        "incorrect-label",
    ]
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
    ]


def test_validate_skip_errors():
    report = validate("data/invalid.csv", skip_errors=["blank-label", "blank-row"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [5, 5, "extra-cell"],
    ]


def test_validate_skip_errors_tags():
    report = validate("data/invalid.csv", skip_errors=["#header"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


def test_validate_invalid_limit_errors():
    report = validate("data/invalid.csv", limit_errors=3)
    assert report.task.partial
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
    ]


def test_validate_structure_errors_with_limit_errors():
    report = validate("data/structure-errors.csv", limit_errors=3)
    assert report.task.partial
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "blank-row"],
        [5, 4, "extra-cell"],
        [5, 5, "extra-cell"],
    ]


@pytest.mark.ci
def test_validate_limit_memory():
    source = lambda: ([integer] for integer in range(1, 100000000))
    schema = {"fields": [{"name": "integer", "type": "integer"}], "primaryKey": "integer"}
    layout = Layout(header=False)
    report = validate(source, schema=schema, layout=layout, limit_memory=50)
    assert report.flatten(["code", "note"]) == [
        ["task-error", 'exceeded memory limit "50MB"']
    ]


@pytest.mark.ci
def test_validate_limit_memory_small():
    source = lambda: ([integer] for integer in range(1, 100000000))
    schema = {"fields": [{"name": "integer", "type": "integer"}], "primaryKey": "integer"}
    layout = Layout(header=False)
    report = validate(source, schema=schema, layout=layout, limit_memory=1)
    assert report.flatten(["code", "note"]) == [
        ["task-error", 'exceeded memory limit "1MB"']
    ]


def test_validate_custom_check():

    # Create check
    class custom(Check):
        def validate_row(self, row):
            yield errors.BlankRowError(
                note="",
                cells=list(map(str, row.values())),
                row_number=row.row_number,
                row_position=row.row_position,
            )

    # Validate resource
    report = validate("data/table.csv", checks=[custom()])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, None, "blank-row"],
        [3, None, "blank-row"],
    ]


def test_validate_custom_check_with_arguments():

    # Create check
    class custom(Check):
        def __init__(self, descriptor=None, *, row_position=None):
            self.setinitial("rowPosition", row_position)
            super().__init__(descriptor)

        def validate_row(self, row):
            yield errors.BlankRowError(
                note="",
                cells=list(map(str, row.values())),
                row_number=row.row_number,
                row_position=self.get("rowPosition") or row.row_position,
            )

    # Validate resource
    report = validate("data/table.csv", checks=[custom(row_position=1)])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [1, None, "blank-row"],
        [1, None, "blank-row"],
    ]


def test_validate_custom_check_function_based():

    # Create check
    def custom(row):
        yield errors.BlankRowError(
            note="",
            cells=list(map(str, row.values())),
            row_number=row.row_number,
            row_position=row.row_position,
        )

    # Validate resource
    report = validate("data/table.csv", checks=[custom])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, None, "blank-row"],
        [3, None, "blank-row"],
    ]


def test_validate_custom_check_bad_name():
    report = validate("data/table.csv", checks=[{"code": "bad"}])
    assert report.flatten(["code", "note"]) == [
        ["check-error", 'cannot create check "bad". Try installing "frictionless-bad"'],
    ]


# Issues


def test_validate_infer_fields_issue_223():
    source = [["name1", "name2"], ["123", "abc"], ["456", "def"], ["789", "ghi"]]
    detector = Detector(schema_patch={"fields": {"name": {"type": "string"}}})
    report = validate(source, detector=detector)
    assert report.valid


def test_validate_infer_fields_issue_225():
    source = [["name1", "name2"], ["123", None], ["456", None], ["789"]]
    detector = Detector(schema_patch={"fields": {"name": {"type": "string"}}})
    report = validate(source, detector=detector)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [49, 50, "constraint-error"],
        [68, 50, "constraint-error"],
        [69, 50, "constraint-error"],
    ]


def test_validate_invalid_table_schema_issue_304():
    source = [["name", "age"], ["Alex", "33"]]
    schema = {"fields": [{"name": "name"}, {"name": "age", "type": "bad"}]}
    report = validate(source, schema=schema)
    assert report.flatten(["code", "note"]) == [
        [
            "field-error",
            "\"{'name': 'age', 'type': 'bad'} is not valid under any of the given schemas\" at \"\" in metadata and at \"anyOf\" in profile",
        ],
    ]


def test_validate_table_is_invalid_issue_312():
    report = validate("data/issue-312.xlsx")
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [None, 5, "blank-label"],
        [5, None, "blank-row"],
    ]


def test_validate_order_fields_issue_313():
    source = "data/issue-313.xlsx"
    layout = Layout(pick_fields=[1, 2, 3, 4, 5])
    schema = {
        "fields": [
            {"name": "Column_1", "type": "string"},
            {"name": "Column_2", "type": "string", "constraints": {"required": True}},
            {"name": "Column_3", "type": "string"},
            {"name": "Column_4", "type": "string"},
            {"name": "Column_5", "type": "string"},
        ]
    }
    detector = Detector(schema_sync=True)
    report = validate(source, layout=layout, schema=schema, detector=detector)
    assert report.valid


def test_validate_missing_local_file_raises_scheme_error_issue_315():
    report = validate("bad-path.csv")
    assert report.flatten(["code", "note"]) == [
        ["scheme-error", "[Errno 2] No such file or directory: 'bad-path.csv'"],
    ]


def test_validate_inline_not_a_binary_issue_349():
    with open("data/table.csv") as source:
        report = validate(source)
        assert report.valid


def test_validate_newline_inside_label_issue_811():
    report = validate("data/issue-811.csv")
    assert report.valid


def test_validate_resource_from_json_format_issue_827():
    report = validate(path="data/table.json")
    assert report.valid


def test_validate_resource_none_is_not_iterable_enum_constraint_issue_833():
    report = validate("data/issue-833.csv", schema="data/issue-833.json")
    assert report.valid


def test_validate_resource_header_row_has_first_number_issue_870():
    report = validate("data/issue-870.xlsx", layout={"limitRows": 5})
    assert report.valid


def test_validate_resource_descriptor_type_invalid():
    report = validate(descriptor="data/table.csv")
    assert report.flatten() == [[1, None, None, "resource-error"]]
