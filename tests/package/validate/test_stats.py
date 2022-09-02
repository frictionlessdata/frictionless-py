import pytest
from copy import deepcopy
from frictionless import Package, platform


# General


DESCRIPTOR_SH = {
    "resources": [
        {
            "name": "resource1",
            "path": "data/table.csv",
            "stats": {
                "sha256": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
                "bytes": 30,
            },
        }
    ]
}


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_package_stats():
    source = deepcopy(DESCRIPTOR_SH)
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_validate_package_stats_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["sha256"] += "a"
    source["resources"][0]["stats"]["bytes"] += 1
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "sha256-count"],
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_package_stats_size():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("sha256")
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_validate_package_stats_size_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["bytes"] += 1
    source["resources"][0]["stats"].pop("sha256")
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_package_stats_hash():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_check_file_package_stats_hash_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    source["resources"][0]["stats"]["sha256"] += "a"
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "sha256-count"],
    ]
