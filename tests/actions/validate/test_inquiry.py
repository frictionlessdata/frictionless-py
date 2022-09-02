import pytest
from frictionless import validate


# General


def test_validate_inquiry():
    report = validate({"tasks": [{"path": "data/table.csv"}]})
    assert report.valid


def test_validate_inquiry_multiple():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        },
    )
    assert report.valid


def test_validate_inquiry_multiple_invalid():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv"},
            ]
        },
    )
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


def test_validate_inquiry_multiple_invalid_with_schema():
    report = validate(
        {
            "tasks": [
                {
                    "path": "data/table.csv",
                    "schema": {
                        "fields": [
                            {"name": "bad", "type": "integer"},
                            {"name": "name", "type": "string"},
                        ]
                    },
                },
                {"path": "data/invalid.csv"},
            ],
        },
    )
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, None, 1, "incorrect-label"],
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


def test_validate_inquiry_with_one_resource_from_descriptor():
    report = validate(
        {
            "tasks": [
                {"resource": "data/resource.json"},
            ]
        },
    )
    assert report.valid


def test_validate_inquiry_with_one_package_from_descriptor():
    report = validate(
        {
            "tasks": [
                {"package": "data/package/datapackage.json"},
            ]
        },
    )
    assert report.valid


def test_validate_inquiry_with_multiple_packages():
    report = validate(
        {
            "tasks": [
                {"package": "data/package/datapackage.json"},
                {"package": "data/invalid/datapackage.json"},
            ]
        },
    )
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]


# Parallel


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        },
        parallel=True,
    )
    assert report.valid


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple_invalid():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv"},
            ]
        },
        parallel=True,
    )
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


@pytest.mark.ci
def test_validate_inquiry_with_multiple_packages_with_parallel():
    report = validate(
        {
            "tasks": [
                {"package": "data/package/datapackage.json"},
                {"package": "data/invalid/datapackage.json"},
            ]
        },
        parallel=True,
    )
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]
