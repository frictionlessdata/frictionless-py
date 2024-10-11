import json

from frictionless import Checklist, Package


def test_package_validate_with_skip_errors():
    ## Test runs on data with two blank-row errors, one primary-key error, see
    # first test case
    test_cases = [
        {"ignore": [], "expect_errors": ["blank-row", "primary-key", "blank-row"]},
        {"ignore": ["primary-key"], "expect_errors": ["blank-row", "blank-row"]},
        {"ignore": ["blank-row"], "expect_errors": ["primary-key"]},
        {"ignore": ["blank-row", "primary-key"], "expect_errors": []},
    ]

    for tc in test_cases:
        with open("data/invalid/datapackage.json") as file:
            package = Package(json.load(file), basepath="data/invalid")
            checklist = Checklist(skip_errors=tc["ignore"])

            report = package.validate(checklist)

            assert report.flatten(["type"]) == [[t] for t in tc["expect_errors"]]
