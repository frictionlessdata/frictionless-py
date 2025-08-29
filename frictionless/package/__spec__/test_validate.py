import json
import pathlib
from copy import deepcopy

import pytest

from frictionless import (
    Checklist,
    Detector,
    FrictionlessException,
    Package,
    Resource,
    Schema,
    fields,
    platform,
)

# General


def test_package_validate():
    package = Package({"resources": [{"name": "name", "path": "data/table.csv"}]})
    report = package.validate()
    assert report.valid


def test_package_validate_from_dict():
    with open("data/package/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/package")
        report = package.validate()
        assert report.valid


def test_package_validate_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/invalid")
        report = package.validate()
        assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key"],
            [2, 4, None, "blank-row"],
        ]


def test_package_validate_from_path():
    package = Package("data/package/datapackage.json")
    report = package.validate()
    assert report.valid


def test_package_validate_from_path_invalid():
    package = Package("data/invalid/datapackage.json")
    report = package.validate()
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


def test_package_validate_with_non_tabular():
    package = Package(
        {
            "resources": [
                {"name": "table", "path": "data/table.csv"},
                {"name": "file", "path": "data/file.txt"},
            ]
        },
    )
    report = package.validate()
    assert report.valid


@pytest.mark.skip
def test_package_validate_invalid_descriptor_path():
    report = Package("bad/datapackage.json").validate()
    error = report.errors[0]
    assert error.type == "package-error"
    assert error.note.count("[Errno 2]")
    assert error.note.count("bad/datapackage.json")


@pytest.mark.skip
def test_package_validate_invalid_package():
    report = Package(
        {"resources": [{"name": "name", "path": "data/table.csv", "schema": "bad"}]}
    ).validate()
    assert report.stats["errors"] == 1
    error = report.errors[0]
    assert error.type == "schema-error"
    assert error.note.count("[Errno 2]")
    assert error.note.count("'bad'")
    assert report.valid


def test_package_validate_invalid_package_standards_v2_strict():
    report = Package.validate_descriptor({"resources": [{"path": "data/table.csv"}]})
    assert report.flatten(["type", "note"]) == [
        ["resource-error", "'name' is a required property"],
    ]


def test_package_validate_invalid_table():
    package = Package({"resources": [{"name": "name", "path": "data/invalid.csv"}]})
    report = package.validate()
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


def test_package_validate_pathlib_source():
    package = Package(pathlib.Path("data/package/datapackage.json"))
    report = package.validate()
    assert report.valid


def test_package_validate_infer():
    package = Package("data/infer/datapackage.json")
    report = package.validate()
    assert report.valid


def test_package_validate_dialect_header_false():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["John", "22"], ["Alex", "33"], ["Paul", "44"]],
                "dialect": {"header": False},
                "schema": {
                    "fields": [
                        {"name": "name", "type": "string"},
                        {"name": "age", "type": "integer"},
                    ]
                },
            }
        ]
    }
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_package_validate_with_schema_as_string():
    package = Package(
        {
            "resources": [
                {"name": "name", "path": "data/table.csv", "schema": "data/schema.json"}
            ]
        }
    )
    report = package.validate()
    assert report.valid


@pytest.mark.skip
def test_package_validate_multiple_package_errors():
    report = Package.validate_descriptor("data/multiple-errors.package.json")
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


def test_package_validate_descriptor_type_package():
    package = Package("data/package/datapackage.json")
    report = package.validate()
    assert report.valid


def test_package_validate_descriptor_type_package_invalid():
    package = Package("data/invalid/datapackage.json")
    report = package.validate()
    assert report.flatten() == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


# Bugs


def test_package_validate_mixed_issue_170():
    package = Package("data/infer/datapackage.json")
    report = package.validate()
    assert report.valid


def test_package_validate_composite_primary_key_unique_issue_215():
    source = {
        "resources": [
            {
                "name": "name",
                "data": [["id1", "id2"], ["a", "1"], ["a", "2"]],
                "schema": {
                    "fields": [
                        {"name": "id1", "type": "string"},
                        {"name": "id2", "type": "string"},
                    ],
                    "primaryKey": ["id1", "id2"],
                },
            }
        ],
    }
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_package_validate_composite_primary_key_not_unique_issue_215():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["id1", "id2"], ["a", "1"], ["a", "1"]],
                "schema": {
                    "fields": [
                        {"name": "id1", "type": "string"},
                        {"name": "id2", "type": "string"},
                    ],
                    "primaryKey": ["id1", "id2"],
                },
            }
        ],
    }
    package = Package(descriptor)
    checklist = Checklist(skip_errors=["duplicate-row"])
    report = package.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, None, "primary-key"],
    ]


def test_package_validate_geopoint_required_constraint_issue_231():
    # We check here that it doesn't raise exceptions
    package = Package("data/geopoint/datapackage.json")
    report = package.validate()
    assert report.valid


def test_package_validate_number_test_issue_232():
    # We check here that it doesn't raise exceptions
    package = Package("data/number/datapackage.json")
    report = package.validate()
    assert not report.valid


def test_package_validate_with_schema_issue_348():
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
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 4, "missing-label"],
        [2, 4, "missing-cell"],
        [3, 4, "missing-cell"],
    ]


@pytest.mark.ci
@pytest.mark.vcr
def test_package_validate_uppercase_format_issue_494():
    package = Package("data/issue-494.package.json")
    report = package.validate()
    assert report.valid
    assert report.stats["tasks"] == 1


def test_validate_package_using_detector_schema_sync_issue_847():
    package = Package(
        resources=[
            Resource(
                data=[["f1"], ["v1"], ["v2"], ["v3"]],
                schema=Schema(
                    fields=[
                        fields.StringField(name="f1"),
                        fields.StringField(name="f2"),
                    ],
                ),
            ),
        ]
    )
    for resource in package.resources:  # type: ignore
        resource.detector = Detector(schema_sync=True)
    report = package.validate()
    assert report.valid


def test_package_validate_with_diacritic_symbol_issue_905():
    package = Package("data/issue-905/datapackage.json")
    report = package.validate()
    assert report.stats["tasks"] == 3


def test_package_validate_with_resource_data_is_a_string_issue_977():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/issue-977.json")
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "package-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert (
        reasons[0].note
        == "'MY_INLINE_DATA' is not of type 'object', 'array' at property 'data'"
    )


def test_package_validate_metadata_errors_with_missing_values_993():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/package-with-missingvalues-993.json")
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "package-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "package-error"
    assert (
        reasons[0].note
        == '"missingValues" should be set as "resource.schema.missingValues"'
    )


def test_package_validate_metadata_errors_with_fields_993():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("data/package-with-fields-993.json")
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "package-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "package-error"
    assert reasons[0].note == '"fields" should be set as "resource.schema.fields"'


def test_package_licenses_required_path_or_name_issue_1290():
    descriptor = {"resources": [], "licenses": [{"title": "title"}]}
    report = Package.validate_descriptor(descriptor)
    assert report.errors[0].note.count('license requires "path" or "name"')


def test_package_validate_with_skip_errors():
    ## Test runs on data with two blank-row errors, one primary-key error, see
    # first test case
    test_cases = [
        {"ignore": [], "expect_errors": ["blank-row", "primary-key", "blank-row"]},
        {"ignore": ["primary-key"], "expect_errors": ["blank-row", "blank-row"]},
        {"ignore": ["blank-row"], "expect_errors": ["primary-key"]},
        {"ignore": ["blank-row", "primary-key"], "expect_errors": []},
    ]

    for tc in test_cases:
        with open("data/invalid/datapackage.json") as file:
            package = Package(json.load(file), basepath="data/invalid")
            checklist = Checklist(skip_errors=tc["ignore"])

            report = package.validate(checklist)

            assert report.flatten(["type"]) == [[t] for t in tc["expect_errors"]]


# Stats

DESCRIPTOR_SH = {
    "resources": [
        {
            "name": "resource1",
            "path": "data/table.csv",
            "hash": "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
            "bytes": 30,
        }
    ]
}


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_validate_stats():
    source = deepcopy(DESCRIPTOR_SH)
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_package_validate_stats_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["hash"] += "a"
    source["resources"][0]["bytes"] += 1
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "hash-count"],
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_validate_stats_size():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0].pop("hash")
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_package_validate_stats_size_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["bytes"] += 1
    source["resources"][0].pop("hash")
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_validate_stats_hash():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0].pop("bytes")
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_package_validate_check_file_package_stats_hash_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0].pop("bytes")
    source["resources"][0]["hash"] += "a"
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "hash-count"],
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
                    {
                        "fields": "next_id",
                        "reference": {"resource": "", "fields": "id"},
                    },
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


def test_package_validate_schema_foreign_key_error():
    descriptor = deepcopy(DESCRIPTOR_FK)
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_package_validate_schema_foreign_key_not_defined():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["schema"]["foreignKeys"]
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_package_validate_schema_foreign_key_self_referenced_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["data"][4]
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [4, None, "foreign-key", ["3", "rome", "4"]],
    ]


def test_package_validate_schema_foreign_key_internal_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][1]["data"][4]
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [5, None, "foreign-key", ["4", "rio", ""]],
    ]


def test_package_validate_schema_foreign_key_internal_resource_violation_non_existent():
    descriptor = deepcopy(DESCRIPTOR_FK)
    descriptor["resources"][1]["data"] = [["label", "population"], [10, 10]]
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [2, None, "foreign-key", ["1", "london", "2"]],
        [3, None, "foreign-key", ["2", "paris", "3"]],
        [4, None, "foreign-key", ["3", "rome", "4"]],
        [5, None, "foreign-key", ["4", "rio", ""]],
    ]


def test_package_validate_schema_multiple_foreign_key():
    descriptor = deepcopy(DESCRIPTOR_FK)
    descriptor["resources"].append(MULTI_FK_RESSOURCE)
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_package_validate_schema_multiple_foreign_key_resource_violation_non_existent():
    descriptor = deepcopy(DESCRIPTOR_FK)
    # remove London
    del descriptor["resources"][0]["data"][1]
    descriptor["resources"].append(MULTI_FK_RESSOURCE)
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells", "note"]) == [
        [
            2,
            None,
            "foreign-key",
            ["1", "2", "1.5"],
            'for "from, to": values "1, 2" not found in the lookup table "cities" as "id, next_id"',
        ],
    ]


def test_package_validate_schema_multiple_foreign_key_violations():
    descriptor = deepcopy(DESCRIPTOR_FK)
    # Add some wrong fks
    descriptor["resources"][0]["data"][3][0] = 5
    descriptor["resources"][0]["data"][4][0] = 6
    descriptor["resources"].append(MULTI_FK_RESSOURCE)
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(
        [
            "rowNumber",
            "fieldNames",
            "fieldCells",
            "referenceName",
            "referenceFieldNames",
        ]
    ) == [
        [3, ["next_id"], ["3"], "", ["id"]],
        [4, ["next_id"], ["4"], "", ["id"]],
        [4, ["id"], ["5"], "people", ["label"]],
        [5, ["id"], ["6"], "people", ["label"]],
        [4, ["from", "to"], ["3", "4"], "cities", ["id", "next_id"]],
    ]


# Bugs


def test_package_validate_using_detector_schema_sync_issue_847():
    package = Package(
        resources=[
            Resource(
                data=[["f1"], ["v1"], ["v2"], ["v3"]],
                schema=Schema(
                    fields=[
                        fields.AnyField(name="f1"),
                        fields.AnyField(name="f2"),
                    ]
                ),
            ),
        ]
    )
    for resource in package.resources:
        resource.detector = Detector(schema_sync=True)
    report = package.validate()
    assert report.valid


# Parallel

# Note: to test parallel validation, do not use foreign keys to prevent an
# automatic fallback on single-core execution


@pytest.mark.ci
def test_package_validate_parallel_from_dict():
    with open("data/datapackage.json") as file:
        package = Package(json.load(file), basepath="data")
        report = package.validate(parallel=True)
        assert report.valid


@pytest.mark.ci
def test_package_validate_parallel_from_dict_invalid():
    with open("data/invalid/datapackage_no_foreign_key.json") as file:
        package = Package(json.load(file), basepath="data/invalid")
        report = package.validate(parallel=True)
        assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key"],
            [2, 4, None, "blank-row"],
        ]


@pytest.mark.ci
def test_package_validate_with_parallel():
    package = Package("data/invalid/datapackage_no_foreign_key.json")
    report = package.validate(parallel=True)
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]
