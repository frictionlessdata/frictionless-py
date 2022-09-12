from copy import deepcopy
from frictionless import Package, Resource, Schema, Detector, fields


# General


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
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_validate_package_schema_foreign_key_not_defined():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["schema"]["foreignKeys"]
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_validate_package_schema_foreign_key_self_referenced_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["data"][4]
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [4, None, "foreign-key", ["3", "rome", "4"]],
    ]


def test_validate_package_schema_foreign_key_internal_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][1]["data"][4]
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [5, None, "foreign-key", ["4", "rio", ""]],
    ]


def test_validate_package_schema_foreign_key_internal_resource_violation_non_existent():
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


def test_validate_package_schema_multiple_foreign_key():
    descriptor = deepcopy(DESCRIPTOR_FK)
    descriptor["resources"].append(MULTI_FK_RESSOURCE)
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_validate_package_schema_multiple_foreign_key_resource_violation_non_existent():
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


def test_validate_package_schema_multiple_foreign_key_violations():
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


def test_validate_package_using_detector_schema_sync_issue_847():
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
