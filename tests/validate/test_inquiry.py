import pytest
from frictionless import validate


# General


def test_validate_inquiry():
    report = validate({"tasks": [{"source": "data/table.csv"}]})
    assert report.valid


def test_validate_inquiry_multiple():
    report = validate(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/matrix.csv"}]},
        nopool=True,
    )
    assert report.valid


def test_validate_inquiry_multiple_invalid():
    report = validate(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/invalid.csv"}]},
        nopool=True,
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


def test_validate_inquiry_multiple_invalid_limit_errors():
    report = validate(
        {
            "tasks": [
                {"source": "data/table.csv"},
                {"source": "data/invalid.csv", "limitErrors": 1},
            ]
        },
        nopool=True,
    )
    assert report.flatten(["tablePosition", "code", "note"]) == [
        [2, "blank-label", ""],
    ]
    assert report.tables[0].flatten(["rowPosition", "fieldPosition", "code"]) == []
    assert report.tables[1].flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
    ]


def test_validate_inquiry_multiple_invalid_with_schema():
    report = validate(
        {
            "tasks": [
                {
                    "source": "data/table.csv",
                    "schema": {"fields": [{"name": "bad"}, {"name": "name"}]},
                },
                {"source": "data/invalid.csv"},
            ],
        },
        nopool=True,
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
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


def test_validate_inquiry_with_one_package():
    report = validate(
        {"tasks": [{"source": "data/package/datapackage.json"}]},
        nopool=True,
    )
    assert report.valid


def test_validate_inquiry_with_multiple_packages():
    report = validate(
        {
            "tasks": [
                {"source": "data/package/datapackage.json"},
                {"source": "data/invalid/datapackage.json"},
            ]
        },
        nopool=True,
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key-error"],
        [4, 4, None, "blank-row"],
    ]


def test_validate_inquiry_with_multiple_packages_with_nopool():
    report = validate(
        {
            "tasks": [
                {"source": "data/package/datapackage.json"},
                {"source": "data/invalid/datapackage.json"},
            ]
        },
        nopool=True,
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key-error"],
        [4, 4, None, "blank-row"],
    ]


# Parallel


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple():
    report = validate(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/matrix.csv"}]}
    )
    assert report.valid


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple_invalid():
    report = validate(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/invalid.csv"}]}
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]
