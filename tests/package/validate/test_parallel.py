import json
import pytest
from frictionless import Package, Checklist, helpers


IS_UNIX = not helpers.is_platform("windows")


@pytest.mark.ci
def test_validate_package_parallel_from_dict():
    with open("data/package/datapackage.json") as file:
        with pytest.warns(UserWarning):
            package = Package(json.load(file), basepath="data/package")
            checklist = Checklist(allow_parallel=True)
            report = package.validate(checklist)
            assert report.valid


@pytest.mark.ci
def test_validate_package_parallel_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/invalid")
        checklist = Checklist(allow_parallel=True)
        report = package.validate(checklist)
        assert report.flatten(
            ["taskPosition", "rowPosition", "fieldPosition", "code"]
        ) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key-error"],
            [2, 4, None, "blank-row"],
        ]


@pytest.mark.ci
def test_validate_package_with_parallel():
    package = Package("data/invalid/datapackage.json")
    checklist = Checklist(allow_parallel=True)
    report = package.validate(checklist)
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key-error"],
        [2, 4, None, "blank-row"],
    ]
