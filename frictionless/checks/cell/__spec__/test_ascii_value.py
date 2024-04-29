import sys

import pytest

from frictionless import Checklist, Resource, checks

# General


def test_validate_ascii_value_845():
    resource = Resource("data/ascii.csv")
    checklist = Checklist(checks=[checks.ascii_value()])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == []


def test_validate_ascii_value_descriptor_845():
    resource = Resource("data/ascii.csv")
    checklist = Checklist.from_descriptor({"checks": [{"type": "ascii-value"}]})
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == []


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
def test_validate_ascii_not_valid_845():
    resource = Resource("data/ascii-notvalid.csv")
    checklist = Checklist(checks=[checks.ascii_value()])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 2, "ascii-value"],
        [2, 3, "ascii-value"],
    ]
