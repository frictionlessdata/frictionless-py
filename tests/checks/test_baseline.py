import pytest

from frictionless import Resource, platform

# General


def test_validate_baseline():
    resource = Resource("data/table.csv")
    report = resource.validate()
    assert report.valid


def test_validate_invalid():
    resource = Resource("data/invalid.csv")
    report = resource.validate()
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


# Stats


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_baseline_stats_hash():
    hash = "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    resource = Resource("data/table.csv", hash=hash)
    report = resource.validate()
    assert report.task.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_baseline_stats_hash_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    resource = Resource("data/table.csv", hash="bad")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        [
            "hash-count",
            'expected is "bad" and actual is "%s"' % hash,
        ],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_baseline_stats_bytes():
    resource = Resource("data/table.csv", bytes=30)
    report = resource.validate()
    assert report.task.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_baseline_stats_bytes_invalid():
    resource = Resource("data/table.csv", bytes=40)
    report = resource.validate()
    assert report.task.error.to_descriptor().get("rowNumber") is None
    assert report.task.error.to_descriptor().get("fieldNumber") is None
    assert report.flatten(["type", "note"]) == [
        ["byte-count", 'expected is "40" and actual is "30"'],
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_baseline_stats_rows():
    resource = Resource("data/table.csv", rows=2)
    report = resource.validate()
    assert report.task.valid


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_validate_baseline_stats_rows_invalid():
    resource = Resource("data/table.csv", rows=3)
    report = resource.validate()
    assert report.task.error.to_descriptor().get("rowNumber") is None
    assert report.task.error.to_descriptor().get("fieldNumber") is None
    assert report.flatten(["type", "note"]) == [
        ["row-count", 'expected is "3" and actual is "2"'],
    ]
