import sys
from typing import List, Optional

import pytest

from frictionless import (
    Detector,
    FrictionlessException,
    Package,
    Resource,
    Schema,
    platform,
)
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


DESCRIPTOR_FK = {
    "name": "name",
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
    resource = TableResource.from_descriptor(descriptor, basepath="data")
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
    resource = TableResource.from_descriptor(descriptor, basepath="data")
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
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_schema_source_remote():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "table.csv",
        "schema": "schema.json",
    }
    resource = TableResource.from_descriptor(descriptor, basepath=BASEURL % "data")
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
        TableResource.from_descriptor(
            {
                "name": "name",
                "path": "data/table.csv",
                "schema": "data/bad.json",
            }
        ).schema
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.note.count("bad.json")


def test_resource_schema_inferred():
    with TableResource(path="data/table.csv") as resource:
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
    with TableResource(path="data/table.csv", schema=schema) as resource:
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
    with TableResource(data=source, detector=detector) as resource:
        for row in resource.row_stream:
            assert row.valid


def test_resource_schema_unique_error():
    source = [["name"], [1], [2], [2]]
    detector = Detector(
        schema_patch={"fields": {"name": {"constraints": {"unique": True}}}}
    )
    with TableResource(data=source, detector=detector) as resource:
        for row in resource.row_stream:
            if row.row_number == 4:
                assert row.valid is False
                assert row.errors[0].type == "unique-error"
                continue
            assert row.valid


def test_resource_schema_primary_key():
    source = [["name"], [1], [2], [3]]
    detector = Detector(schema_patch={"primaryKey": ["name"]})
    with TableResource(data=source, detector=detector) as resource:
        for row in resource.row_stream:
            assert row.valid


def test_resource_schema_primary_key_error():
    source = [["name"], [1], [2], [2]]
    detector = Detector(schema_patch={"primaryKey": ["name"]})
    with TableResource(data=source, detector=detector) as resource:
        for row in resource.row_stream:
            if row.row_number == 4:
                assert row.valid is False
                assert row.errors[0].type == "primary-key"
                continue
            assert row.valid


def test_resource_schema_foreign_keys():
    resource = TableResource.from_descriptor(DESCRIPTOR_FK)
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
    resource = TableResource.from_descriptor(
        DESCRIPTOR_FK, path="data/nested-invalid.csv"
    )
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


def _handle_expected_validity_and_errors(
    resource: Resource,
    expected_validity: List[bool],
    expected_errors: List[Optional[str]],
):
    rows = resource.read_rows()
    print(rows)
    for i, (expected_valid, expected_error) in enumerate(
        zip(expected_validity, expected_errors)
    ):
        assert rows[i].valid == expected_valid
        if expected_error:
            assert rows[i].errors[0].type == expected_error


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "valid_self_referencing",
            "data": [
                ["eventID", "parentEventID"],
                ["1", ""],
                ["2", "1"],
                ["3", "1"],
                ["4", "2"],
                ["5", "3"],
            ],
            "expected_validity": [True, True, True, True, True],
            "expected_errors": [None, None, None, None, None],
        },
        {
            "name": "invalid_self_referencing",
            "data": [
                ["eventID", "parentEventID"],
                ["1", ""],
                ["2", "1"],
                ["3", "999"],  # Invalid reference to non-existent parent
            ],
            "expected_validity": [True, True, False],
            "expected_errors": [None, None, "foreign-key"],
        },
    ],
)
def test_resource_schema_self_referencing_foreign_keys(test_case):
    """Test self-referencing foreign keys with explicit resource reference"""
    descriptor = {
        "name": "event",
        "data": test_case["data"],
        "schema": {
            "fields": [
                {"name": "eventID", "type": "string"},
                {"name": "parentEventID", "type": "string"},
            ],
            "primaryKey": ["eventID"],
            "foreignKeys": [
                {
                    "fields": "parentEventID",
                    "reference": {"resource": "event", "fields": "eventID"},
                }
            ],
        },
    }

    resource = TableResource.from_descriptor(descriptor)

    _handle_expected_validity_and_errors(
        resource, test_case["expected_validity"], test_case["expected_errors"]
    )

    # Same test but with implicit self-reference
    descriptor["schema"]["foreignKeys"][0]["reference"].pop("resource", None)

    resource = TableResource.from_descriptor(descriptor)

    _handle_expected_validity_and_errors(
        resource, test_case["expected_validity"], test_case["expected_errors"]
    )


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "valid_circular_references",
            "data_a": [
                ["id", "name", "ref_b"],
                [1, "Item A1", 10],
                [2, "Item A2", 20],
                [3, "Item A3", ""],
            ],
            "data_b": [
                ["id", "name", "ref_a"],
                [10, "Item B1", 1],
                [20, "Item B2", 2],
                [30, "Item B3", ""],
            ],
            "expected_validity_a": [True, True, True],
            "expected_validity_b": [True, True, True],
            "expected_errors_a": [None, None, None],
            "expected_errors_b": [None, None, None],
        },
        {
            "name": "invalid_circular_references",
            "data_a": [
                ["id", "name", "ref_b"],
                [1, "Item A1", 10],
                [2, "Item A2", 999],  # Invalid reference
            ],
            "data_b": [
                ["id", "name", "ref_a"],
                [10, "Item B1", 1],
                [20, "Item B2", 888],  # Invalid reference
            ],
            "expected_validity_a": [True, False],
            "expected_validity_b": [True, False],
            "expected_errors_a": [None, "foreign-key"],
            "expected_errors_b": [None, "foreign-key"],
        },
    ],
)
def test_resource_schema_circular_foreign_keys(test_case):
    """Test circular foreign keys between two resources"""
    package_descriptor = {
        "name": "circular-package",
        "resources": [
            {
                "name": "resource_a",
                "data": test_case["data_a"],
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                        {"name": "ref_b", "type": "integer"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": "ref_b",
                            "reference": {"resource": "resource_b", "fields": "id"},
                        }
                    ],
                },
            },
            {
                "name": "resource_b",
                "data": test_case["data_b"],
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                        {"name": "ref_a", "type": "integer"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": "ref_a",
                            "reference": {"resource": "resource_a", "fields": "id"},
                        }
                    ],
                },
            },
        ],
    }

    package = Package.from_descriptor(package_descriptor)

    _handle_expected_validity_and_errors(
        package.get_resource("resource_a"),
        test_case["expected_validity_a"],
        test_case["expected_errors_a"],
    )
    _handle_expected_validity_and_errors(
        package.get_resource("resource_b"),
        test_case["expected_validity_b"],
        test_case["expected_errors_b"],
    )
