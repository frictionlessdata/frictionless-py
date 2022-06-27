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


def test_inquiry_validate_multiple_invalid_limit_errors():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv", "checklist": {"limitErrors": 1}},
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


def test_inquiry_validate_multiple_invalid_with_schema():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {
                    "path": "data/table.csv",
                    "schema": {"fields": [{"name": "bad"}, {"name": "name"}]},
                },
                {"path": "data/invalid.csv"},
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


def test_inquiry_validate_with_one_resource_from_descriptor():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"descriptor": "data/resource.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.valid


def test_inquiry_validate_with_one_package_from_descriptor():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"descriptor": "data/package/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.valid


def test_inquiry_validate_with_multiple_packages():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"descriptor": "data/package/datapackage.json"},
                {"descriptor": "data/invalid/datapackage.json"},
            ]
        },
    )
    report = inquiry.validate()
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]


# Parallel


@pytest.mark.skip
@pytest.mark.ci
def test_inquiry_validate_parallel_multiple():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"source": "data/table.csv"},
                {"source": "data/matrix.csv"},
            ]
        },
    )
    report = inquiry.validate(parallel=True)
    assert report.valid


@pytest.mark.skip
@pytest.mark.ci
def test_inquiry_validate_parallel_multiple_invalid():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"source": "data/table.csv"},
                {"source": "data/invalid.csv"},
            ]
        },
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


@pytest.mark.skip
@pytest.mark.ci
def test_inquiry_validate_with_multiple_packages_with_parallel():
    inquiry = Inquiry.from_descriptor(
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
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]
