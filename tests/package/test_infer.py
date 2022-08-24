import pytest
from frictionless import Package, Resource, platform


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_infer():
    package = Package("data/infer/*.csv")
    package.infer(stats=True)
    assert package.to_descriptor() == {
        "resources": [
            {
                "name": "data",
                "path": "data/infer/data.csv",
                "type": "table",
                "scheme": "file",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "description", "type": "string"},
                        {"name": "amount", "type": "number"},
                    ]
                },
                "stats": {
                    "md5": "c028f525f314c49ea48ed09e82292ed2",
                    "sha256": "08b4645fd105c74fbb752c4cf6a1a995452178953bb874697830002474f9538f",
                    "bytes": 114,
                    "fields": 4,
                    "rows": 2,
                },
            },
            {
                "name": "data2",
                "path": "data/infer/data2.csv",
                "type": "table",
                "scheme": "file",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "parent", "type": "string"},
                        {"name": "comment", "type": "string"},
                    ]
                },
                "stats": {
                    "md5": "cb4a683d8eecb72c9ac9beea91fd592e",
                    "sha256": "c58f34fe7961113baf24fb45f4b9fcfff9ceae6274373fd9d3c84be540075406",
                    "bytes": 60,
                    "fields": 2,
                    "rows": 3,
                },
            },
        ],
    }


def test_package_infer_with_basepath():
    package = Package("*.csv", basepath="data/infer")
    package.infer()
    assert len(package.resources) == 2
    assert package.resources[0].path == "data.csv"
    assert package.resources[1].path == "data2.csv"


def test_package_infer_multiple_paths():
    package = Package(["data.csv", "data2.csv"], basepath="data/infer")
    package.infer()
    assert len(package.resources) == 2
    assert package.resources[0].path == "data.csv"
    assert package.resources[1].path == "data2.csv"


def test_package_infer_non_utf8_file():
    package = Package("data/table-with-accents.csv")
    package.infer()
    assert len(package.resources) == 1
    assert package.resources[0].encoding == "iso8859-1"


def test_package_infer_empty_file():
    package = Package("data/empty.csv")
    package.infer()
    assert len(package.resources) == 1
    assert package.resources[0].stats.bytes == None


# Bugs


def test_package_infer_duplicate_resource_names_issue_530():
    package = Package(
        resources=[
            Resource(path="data/chunk1.csv"),
            Resource(path="data/chunk2.csv"),
            Resource(path="data/tables/chunk1.csv"),
            Resource(path="data/tables/chunk2.csv"),
        ]
    )
    package.infer()
    assert len(set(package.resource_names)) == 4
    assert package.resource_names == ["chunk1", "chunk2", "chunk12", "chunk22"]
