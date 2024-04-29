import pytest

from frictionless import validate
from frictionless.exception import FrictionlessException

# General


def test_validate():
    report = validate("data/table.csv")
    assert report.valid


def test_validate_invalid():
    report = validate("data/invalid.csv")
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


def test_validate_invalid_source():
    report = validate("bad.json", type="resource")
    assert report.stats["errors"] == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "resource-error"
    assert note.count("[Errno 2]") and note.count("bad.json")


def test_validate_invalid_resource():
    report = validate({"name": "name", "path": "data/table.csv", "schema": "bad"})
    assert report.stats["errors"] == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "schema-error"
    assert note.count("[Errno 2]") and note.count("bad")


@pytest.mark.skip
def test_validate_forbidden_value_task_error():
    descriptor = {
        "path": "data/table.csv",
        "checklist": {
            "checks": [
                {"type": "forbidden-value", "fieldName": "bad", "forbidden": [2]},
            ]
        },
    }
    report = validate(descriptor)
    assert report.flatten(["type", "note"]) == [
        ["check-error", "'values' is a required property"],
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


# TODO: recover
@pytest.mark.skip
def test_validate_package_invalid_json_issue_192():
    report = validate("data/invalid.json", type="package")
    assert report.flatten(["type", "note"]) == [
        [
            "package-error",
            'cannot retrieve metadata "data/invalid.json" because "Expecting property name enclosed in double quotes: line 2 column 5 (char 6)"',
        ]
    ]


def test_validate_package_single_resource_issue_221():
    report = validate("data/datapackage.json", resource_name="number-two")
    assert report.valid


def test_validate_package_single_resource_wrong_resource_name_issue_221():
    with pytest.raises(FrictionlessException) as excinfo:
        validate("data/datapackage.json", resource_name="bad")
    error = excinfo.value.error
    assert error.note.count('"bad"')


def test_validate_multiple_files_issue_850():
    report = validate("data/package/*.csv")
    assert report.stats["tasks"] == 2
