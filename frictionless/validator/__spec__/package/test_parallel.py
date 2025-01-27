import json

import pytest

from frictionless import Package

# General

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
