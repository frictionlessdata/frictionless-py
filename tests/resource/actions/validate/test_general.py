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
    assert report["stats"]["errors"] == 1
    [[code, note]] = report.flatten(["code", "note"])
    assert code == "resource-error"
    assert note.count("[Errno 2]") and note.count("bad.json")


def test_validate_invalid_resource():
    report = validate({"path": "data/table.csv", "schema": "bad"})
    assert report["stats"]["errors"] == 1
    [[code, note]] = report.flatten(["code", "note"])
    assert code == "schema-error"
    assert note.count("[Errno 2]") and note.count("bad")


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


def test_validate_resource_descriptor_type_invalid():
    report = validate(descriptor="data/table.csv")
    assert report.flatten() == [[1, None, None, "resource-error"]]


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
    assert report["stats"]["errors"] == 1
    [[code, note]] = report.flatten(["code", "note"])
    assert code == "scheme-error"
    assert note.count("[Errno 2]") and note.count("bad-path.csv")


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


def test_validate_resource_array_path_issue_991():
    report = validate("data/issue-991.resource.json")
    assert report.flatten(["code", "note"]) == [
        [
            "scheme-error",
            'Multipart resource requires "multipart" scheme but "file" is set',
        ],
    ]


def test_validate_resource_duplicate_labels_with_sync_schema_issue_910():
    detector = Detector(schema_sync=True)
    report = validate(
        "data/duplicate-column.csv",
        schema="data/duplicate-column-schema.json",
        detector=detector,
    )
    assert report.flatten(["code", "note"]) == [
        [
            "general-error",
            'Duplicate labels in header is not supported with "schema_sync"',
        ],
    ]
