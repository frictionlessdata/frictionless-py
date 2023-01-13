import pytest
from frictionless import Inquiry


# Sequential


def test_inquiry_validate():
    inquiry = Inquiry.from_descriptor({"tasks": [{"path": "data/table.csv"}]})
    report = inquiry.validate()
    assert report.valid


def test_inquiry_validate_multiple():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.valid


def test_inquiry_validate_multiple_invalid():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv"},
            ]
        },
    )
    report = inquiry.validate()
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


def test_inquiry_validate_multiple_invalid_with_schema():
    inquiry = Inquiry.from_descriptor(
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
    report = inquiry.validate()
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


def test_inquiry_validate_with_one_resource_from_descriptor():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"resource": "data/resource.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.valid


def test_inquiry_validate_with_one_package_from_descriptor():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"package": "data/package/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.valid


def test_inquiry_validate_with_multiple_packages():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"package": "data/package/datapackage.json"},
                {"package": "data/invalid/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]


# Parallel


# TODO: recover -- it randomly/sometimes fails on CI because of a time limit
@pytest.mark.skip
@pytest.mark.ci
def test_inquiry_validate_parallel_multiple():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        },
    )
    report = inquiry.validate(parallel=True)
    assert report.valid


# TODO: recover -- it randomly/sometimes fails on CI because of a time limit
@pytest.mark.skip
@pytest.mark.ci
def test_inquiry_validate_parallel_multiple_invalid():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv"},
            ]
        },
    )
    report = inquiry.validate(parallel=True)
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


@pytest.mark.skip
@pytest.mark.ci
def test_inquiry_validate_with_multiple_packages_with_parallel():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"package": "data/package/datapackage.json"},
                {"package": "data/invalid/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate(parallel=True)
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]
