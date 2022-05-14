import pytest
from frictionless import Inquiry


# General


def test_validate_inquiry():
    inquiry = Inquiry({"tasks": [{"source": "data/table.csv"}]})
    report = inquiry.validate()
    assert report.valid


def test_validate_inquiry_multiple():
    inquiry = Inquiry(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/matrix.csv"}]},
    )
    report = inquiry.validate()
    assert report.valid


def test_validate_inquiry_multiple_invalid():
    inquiry = Inquiry(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/invalid.csv"}]},
    )
    report = inquiry.validate()
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
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
    inquiry = Inquiry(
        {
            "tasks": [
                {"source": "data/table.csv"},
                {"source": "data/invalid.csv", "limitErrors": 1},
            ]
        },
    )
    report = inquiry.validate()
    assert report.flatten(["taskPosition", "code", "note"]) == [
        [2, "blank-label", ""],
    ]
    assert report.tasks[0].flatten(["rowPosition", "fieldPosition", "code"]) == []
    assert report.tasks[1].flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
    ]


def test_validate_inquiry_multiple_invalid_with_schema():
    inquiry = Inquiry(
        {
            "tasks": [
                {
                    "source": "data/table.csv",
                    "schema": {"fields": [{"name": "bad"}, {"name": "name"}]},
                },
                {"source": "data/invalid.csv"},
            ],
        },
    )
    report = inquiry.validate()
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
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
    inquiry = Inquiry(
        {"tasks": [{"source": "data/package/datapackage.json"}]},
    )
    report = inquiry.validate()
    assert report.valid


def test_validate_inquiry_with_multiple_packages():
    inquiry = Inquiry(
        {
            "tasks": [
                {"source": "data/package/datapackage.json"},
                {"source": "data/invalid/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key-error"],
        [4, 4, None, "blank-row"],
    ]


# Parallel


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple():
    inquiry = Inquiry(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/matrix.csv"}]},
    )
    report = inquiry.validate(parallel=True)
    assert report.valid


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple_invalid():
    inquiry = Inquiry(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/invalid.csv"}]},
    )
    report = inquiry.validate(parallel=True)
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
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
    inquiry = Inquiry(
        {
            "tasks": [
                {"source": "data/package/datapackage.json"},
                {"source": "data/invalid/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate(parallel=True)
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key-error"],
        [4, 4, None, "blank-row"],
    ]
