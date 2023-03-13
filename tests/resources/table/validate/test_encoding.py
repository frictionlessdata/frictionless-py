import pytest
from frictionless import Resource, platform


# General


def test_resource_validate_encoding():
    resource = Resource("data/table.csv", encoding="utf-8")
    report = resource.validate()
    assert report.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_validate_encoding_invalid():
    resource = Resource("data/latin1.csv", encoding="utf-8")
    report = resource.validate()
    assert not report.valid
    assert report.flatten(["type", "note"]) == [
        [
            "encoding-error",
            "'utf-8' codec can't decode byte 0xa9 in position 20: invalid start byte",
        ],
    ]
