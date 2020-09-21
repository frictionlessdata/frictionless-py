import pytest
from frictionless import validate


# General


def test_validate():
    report = validate({"tasks": [{"source": "data/table.csv"}]})
    assert report.valid


@pytest.mark.ci
def test_validate_multiple():
    report = validate(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/matrix.csv"}]}
    )
    assert report.valid


@pytest.mark.ci
def test_validate_multiple_invalid():
    report = validate(
        {"tasks": [{"source": "data/table.csv"}, {"source": "data/invalid.csv"}]}
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [2, None, 3, "blank-header"],
        [2, None, 4, "duplicate-header"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


@pytest.mark.ci
def test_validate_multiple_invalid_limit_errors():
    report = validate(
        {
            "tasks": [
                {"source": "data/table.csv"},
                {"source": "data/invalid.csv", "limitErrors": 1},
            ]
        }
    )
    assert report.flatten(["tablePosition", "code", "note"]) == [
        [2, "blank-header", ""],
    ]
    assert report.tables[0].flatten(["rowPosition", "fieldPosition", "code"]) == []
    assert report.tables[1].flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-header"],
    ]


@pytest.mark.ci
def test_validate_multiple_invalid_with_schema():
    report = validate(
        {
            "tasks": [
                {
                    "source": "data/table.csv",
                    "schema": {"fields": [{"name": "bad"}, {"name": "name"}]},
                },
                {"source": "data/invalid.csv"},
            ],
        }
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [1, None, 1, "non-matching-header"],
        [2, None, 3, "blank-header"],
        [2, None, 4, "duplicate-header"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


@pytest.mark.ci
def test_validate_with_one_package():
    report = validate({"tasks": [{"source": "data/package/datapackage.json"}]})
    assert report.valid


@pytest.mark.ci
def test_validate_with_multiple_packages():
    report = validate(
        {
            "tasks": [
                {"source": "data/package/datapackage.json"},
                {"source": "data/invalid/datapackage.json"},
            ]
        }
    )
    assert report.flatten(["tablePosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key-error"],
        [4, 4, None, "blank-row"],
    ]
