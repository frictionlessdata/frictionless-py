import json
import pytest
from frictionless import Package


# General


@pytest.mark.ci
def test_validate_package_parallel_from_dict():
    with open("data/package/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/package")
        report = package.validate(parallel=True)
        assert report.valid


@pytest.mark.ci
def test_validate_package_parallel_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/invalid")
        report = package.validate(parallel=True)
        assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key"],
            [2, 4, None, "blank-row"],
        ]


@pytest.mark.ci
def test_validate_package_with_parallel():
    package = Package("data/invalid/datapackage.json")
    report = package.validate(parallel=True)
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]
