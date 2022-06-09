import pytest
from copy import deepcopy
from frictionless import Package, helpers


# General


DESCRIPTOR_SH = {
    "resources": [
        {
            "name": "resource1",
            "path": "data/table.csv",
            "hashing": "sha256",
            "stats": {
                "hash": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
                "bytes": 30,
            },
        }
    ]
}


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_validate_package_stats():
    source = deepcopy(DESCRIPTOR_SH)
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_validate_package_stats_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["hash"] += "a"
    source["resources"][0]["stats"]["bytes"] += 1
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "hash-count"],
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_validate_package_stats_size():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("hash")
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_validate_package_stats_size_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["bytes"] += 1
    source["resources"][0]["stats"].pop("hash")
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "byte-count"],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_validate_package_stats_hash():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    package = Package(source)
    report = package.validate()
    assert report.valid


def test_check_file_package_stats_hash_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    source["resources"][0]["stats"]["hash"] += "a"
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "hash-count"],
    ]


def test_check_file_package_stats_hash_not_supported_algorithm():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["hashing"] = "bad"
    source["resources"][0]["stats"].pop("bytes")
    package = Package(source)
    report = package.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "hashing-error"],
    ]
