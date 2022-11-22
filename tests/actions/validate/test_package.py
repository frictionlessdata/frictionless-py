import json
import pytest
import pathlib
from copy import deepcopy
from frictionless import Package, Resource, Schema, Detector
from frictionless import system, fields, validate, platform


# General


def test_validate_package():
    report = validate({"resources": [{"path": "data/table.csv"}]})
    assert report.valid


def test_validate_package_from_dict():
    with open("data/package/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/package")
        assert report.valid


def test_validate_package_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/invalid")
        assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key"],
            [2, 4, None, "blank-row"],
        ]


def test_validate_package_from_path():
    report = validate("data/package/datapackage.json")
    assert report.valid


def test_validate_package_from_path_invalid():
    report = validate("data/invalid/datapackage.json")
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


def test_validate_package_with_non_tabular():
    report = validate(
        {
            "resources": [
                {"path": "data/table.csv"},
                {"path": "data/file.txt"},
            ]
        },
    )
    assert report.valid


def test_validate_package_invalid_descriptor_path():
    report = validate("bad/datapackage.json")
    error = report.errors[0]
    assert error.type == "package-error"
    assert error.note.count("[Errno 2]")
    assert error.note.count("bad/datapackage.json")


def test_validate_package_invalid_package():
    report = validate({"resources": [{"path": "data/table.csv", "schema": "bad"}]})
    assert report.stats.errors == 1
    error = report.errors[0]
    assert error.type == "schema-error"
    assert error.note.count("[Errno 2]")
    assert error.note.count("'bad'")


def test_validate_package_invalid_package_standards_v2_strict():
    with system.use_context(standards="v2-strict"):
        report = validate({"resources": [{"path": "data/table.csv"}]})
    assert report.flatten(["type", "note"]) == [
        ["resource-error", 'property "name" is required by standards "v2-strict"'],
        ["resource-error", 'property "type" is required by standards "v2-strict"'],
        ["resource-error", 'property "scheme" is required by standards "v2-strict"'],
        ["resource-error", 'property "format" is required by standards "v2-strict"'],
        ["resource-error", 'property "encoding" is required by standards "v2-strict"'],
        ["resource-error", 'property "mediatype" is required by standards "v2-strict"'],
    ]


def test_validate_package_invalid_table():
    report = validate({"resources": [{"path": "data/invalid.csv"}]})
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


def test_validate_package_pathlib_source():
    report = validate(pathlib.Path("data/package/datapackage.json"))
    assert report.valid


def test_validate_package_infer():
    report = validate("data/infer/datapackage.json")
    assert report.valid


def test_validate_package_dialect_header_false():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["John", "22"], ["Alex", "33"], ["Paul", "44"]],
                "schema": {
                    "fields": [
                        {"name": "name", "type": "string"},
                        {"name": "age", "type": "integer"},
                    ]
                },
                "dialect": {"header": False},
            }
        ]
    }
    report = validate(descriptor)
    assert report.valid


def test_validate_package_with_schema_as_string():
    report = validate(
        {"resources": [{"path": "data/table.csv", "schema": "data/schema.json"}]}
    )
    assert report.valid


def test_validate_package_multiple_package_errors():
    report = validate("data/multiple-errors.package.json")
    assert report.flatten(["type", "message"]) == [
        [
            "package-error",
            "The data package has an error: names of the resources are not unique",
        ],
        [
            "package-error",
            'The data package has an error: property "created" is not valid "datetime"',
        ],
    ]


# Schema


DESCRIPTOR_FK = {
    "resources": [
        {
            "name": "cities",
            "data": [
                ["id", "name", "next_id"],
                [1, "london", 2],
                [2, "paris", 3],
                [3, "rome", 4],
                [4, "rio", None],
            ],
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                    {"name": "next_id", "type": "integer"},
                ],
                "foreignKeys": [
                    {"fields": "next_id", "reference": {"resource": "", "fields": "id"}},
                    {
                        "fields": "id",
                        "reference": {"resource": "people", "fields": "label"},
                    },
                ],
            },
        },
        {
            "name": "people",
            "data": [["label", "population"], [1, 8], [2, 2], [3, 3], [4, 6]],
        },
    ],
}

MULTI_FK_RESSOURCE = {
    "name": "travel_time",
    "data": [["from", "to", "hours"], [1, 2, 1.5], [2, 3, 8], [3, 4, 18]],
    "schema": {
        "fields": [
            {"name": "from", "type": "integer"},
            {"name": "to", "type": "integer"},
            {"name": "hours", "type": "number"},
        ],
        "foreignKeys": [
            {
                "fields": ["from", "to"],
                "reference": {"resource": "cities", "fields": ["id", "next_id"]},
            }
        ],
    },
}


def test_validate_package_schema_foreign_key_error():
    descriptor = deepcopy(DESCRIPTOR_FK)
    report = validate(descriptor)
    assert report.valid


def test_validate_package_schema_foreign_key_not_defined():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["schema"]["foreignKeys"]
    report = validate(descriptor)
    assert report.valid


def test_validate_package_schema_foreign_key_self_referenced_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["data"][4]
    report = validate(descriptor)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [4, None, "foreign-key", ["3", "rome", "4"]],
    ]


def test_validate_package_schema_foreign_key_internal_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][1]["data"][4]
    report = validate(descriptor)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [5, None, "foreign-key", ["4", "rio", ""]],
    ]


def test_validate_package_schema_foreign_key_internal_resource_violation_non_existent():
    descriptor = deepcopy(DESCRIPTOR_FK)
    descriptor["resources"][1]["data"] = [["label", "population"], [10, 10]]
    report = validate(descriptor)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [2, None, "foreign-key", ["1", "london", "2"]],
        [3, None, "foreign-key", ["2", "paris", "3"]],
        [4, None, "foreign-key", ["3", "rome", "4"]],
        [5, None, "foreign-key", ["4", "rio", ""]],
    ]


def test_validate_package_schema_multiple_foreign_key():
    descriptor = deepcopy(DESCRIPTOR_FK)
    descriptor["resources"].append(MULTI_FK_RESSOURCE)
    report = validate(descriptor)
    assert report.valid


def test_validate_package_schema_multiple_foreign_key_resource_violation_non_existent():
    descriptor = deepcopy(DESCRIPTOR_FK)
    # remove London
    del descriptor["resources"][0]["data"][1]
    descriptor["resources"].append(MULTI_FK_RESSOURCE)
    report = validate(descriptor)
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells", "note"]) == [
        [
            2,
            None,
            "foreign-key",
            ["1", "2", "1.5"],
            'for "from, to": values "1, 2" not found in the lookup table "cities" as "id, next_id"',
        ],
    ]


# Stats

DESCRIPTOR_SH = {
    "resources": [
        {
            "name": "resource1",
            "path": "data/table.csv",
            "stats": {
                "sha256": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
                "bytes": 30,
            },
        }
    ]
}


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_package_stats():
    source = deepcopy(DESCRIPTOR_SH)
    report = validate(source)
    assert report.valid


def test_validate_package_stats_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["sha256"] += "a"
    source["resources"][0]["stats"]["bytes"] += 1
    report = validate(source)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "sha256-count"],
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_package_stats_size():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("sha256")
    report = validate(source)
    assert report.valid


def test_validate_package_stats_size_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["bytes"] += 1
    source["resources"][0]["stats"].pop("sha256")
    report = validate(source)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_package_stats_hash():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    report = validate(source)
    assert report.valid


def test_check_file_package_stats_hash_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    source["resources"][0]["stats"]["sha256"] += "a"
    report = validate(source)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "sha256-count"],
    ]


# Parallel


@pytest.mark.ci
def test_validate_package_parallel_from_dict():
    with open("data/package/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/package", parallel=True)
        assert report.valid


@pytest.mark.ci
def test_validate_package_parallel_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/invalid", parallel=True)
        assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key"],
            [2, 4, None, "blank-row"],
        ]


@pytest.mark.ci
def test_validate_package_with_parallel():
    report = validate("data/invalid/datapackage.json", parallel=True)
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


def test_validate_package_descriptor_type_package():
    report = validate("data/package/datapackage.json")
    assert report.valid


def test_validate_package_descriptor_type_package_invalid():
    report = validate("data/invalid/datapackage.json")
    assert report.flatten() == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


# Bugs


def test_validate_package_mixed_issue_170():
    report = validate("data/infer/datapackage.json")
    assert report.valid


def test_validate_package_invalid_json_issue_192():
    report = validate("data/invalid.json", type="package")
    assert report.flatten(["type", "note"]) == [
        [
            "package-error",
            'cannot retrieve metadata "data/invalid.json" because "Expecting property name enclosed in double quotes: line 2 column 5 (char 6)"',
        ]
    ]


def test_validate_package_composite_primary_key_unique_issue_215():
    source = {
        "resources": [
            {
                "name": "name",
                "data": [["id1", "id2"], ["a", "1"], ["a", "2"]],
                "schema": {
                    "fields": [
                        {"name": "id1", "type": "string"},
                        {"name": "id2", "type": "integer"},
                    ],
                    "primaryKey": ["id1", "id2"],
                },
            }
        ],
    }
    report = validate(source)
    assert report.valid


def test_validate_package_composite_primary_key_not_unique_issue_215():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["id1", "id2"], ["a", "1"], ["a", "1"]],
                "schema": {
                    "fields": [
                        {"name": "id1", "type": "string"},
                        {"name": "id2", "type": "integer"},
                    ],
                    "primaryKey": ["id1", "id2"],
                },
            }
        ],
    }
    report = validate(descriptor, skip_errors=["duplicate-row"])
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, None, "primary-key"],
    ]


def test_validate_package_geopoint_required_constraint_issue_231():
    # We check here that it doesn't raise exceptions
    report = validate("data/geopoint/datapackage.json")
    assert report.valid


def test_validate_package_number_test_issue_232():
    # We check here that it doesn't raise exceptions
    report = validate("data/number/datapackage.json")
    assert not report.valid


def test_validate_package_with_schema_issue_348():
    descriptor = {
        "resources": [
            {
                "name": "people",
                "data": [
                    ["id", "name", "surname"],
                    ["p1", "Tom", "Hanks"],
                    ["p2", "Meryl", "Streep"],
                ],
                "schema": {
                    "fields": [
                        {"name": "id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "surname", "type": "string"},
                        {"name": "dob", "type": "date"},
                    ]
                },
            }
        ]
    }
    report = validate(descriptor)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 4, "missing-label"],
        [2, 4, "missing-cell"],
        [3, 4, "missing-cell"],
    ]


@pytest.mark.ci
@pytest.mark.vcr
def test_validate_package_uppercase_format_issue_494():
    report = validate("data/issue-494.package.json")
    assert report.valid
    assert report.stats.tasks == 1


def test_validate_package_using_detector_schema_sync_issue_847():
    package = Package(
        resources=[
            Resource(
                data=[["f1"], ["v1"], ["v2"], ["v3"]],
                schema=Schema(
                    fields=[fields.StringField(name="f1"), fields.StringField(name="f2")],
                ),
            ),
        ]
    )
    for resource in package.resources:  # type: ignore
        resource.detector = Detector(schema_sync=True)
    report = package.validate()
    assert report.valid


def test_validate_package_with_diacritic_symbol_issue_905():
    report = validate("data/issue-905/datapackage.json")
    assert report.stats.tasks == 3


def test_validate_package_with_resource_data_is_a_string_issue_977():
    report = validate("data/issue-977.json", type="package")
    assert report.flatten(["type", "note"]) == [
        [
            "resource-error",
            "'MY_INLINE_DATA' is not of type 'object', 'array' at property 'data'",
        ],
    ]


def test_validate_package_single_resource_221():
    report = validate("data/datapackage.json", resource_name="number-two")
    assert report.valid


def test_validate_package_single_resource_wrong_resource_name_221():
    report = validate("data/datapackage.json", resource_name="number-twoo")
    assert report.flatten(["type", "message"]) == [
        [
            "package-error",
            'The data package has an error: resource "number-twoo" does not exist',
        ]
    ]
