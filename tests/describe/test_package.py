import pytest
from frictionless import describe, helpers


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_describe_package():
    package = describe("data/chunk*.csv")
    assert package.metadata_valid
    assert package == {
        "profile": "data-package",
        "resources": [
            {
                "path": "data/chunk1.csv",
                "profile": "tabular-data-resource",
                "name": "chunk1",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "innerpath": "",
                "compression": "",
                "control": {"newline": ""},
                "dialect": {},
                "layout": {},
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
                "stats": {
                    "hash": "8fff9d97e5c0cb77b7c469ec37c8e766",
                    "bytes": 18,
                    "fields": 2,
                    "rows": 1,
                },
            },
            {
                "path": "data/chunk2.csv",
                "profile": "tabular-data-resource",
                "name": "chunk2",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "innerpath": "",
                "compression": "",
                "control": {"newline": ""},
                "dialect": {},
                "layout": {},
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
                "stats": {
                    "hash": "ebfa07d04a148a92a18078f78468694d",
                    "bytes": 20,
                    "fields": 2,
                    "rows": 1,
                },
            },
        ],
    }


def test_describe_package_basepath():
    package = describe("chunk*.csv", basepath="data")
    assert package.get_resource("chunk1").path == "chunk1.csv"
    assert package.get_resource("chunk2").path == "chunk2.csv"
    assert package.get_resource("chunk1").basepath == "data"
    assert package.get_resource("chunk2").basepath == "data"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_describe_package_hashing():
    package = describe("data/chunk*.csv", hashing="sha256")
    assert package.get_resource("chunk1").hashing == "sha256"
    assert package.get_resource("chunk2").hashing == "sha256"
    assert (
        package.get_resource("chunk1").stats["hash"]
        == "3872c98bd72eb4a91ac666f7758cd83da904c61a35178ca1ce9e10d6b009cd21"
    )
    assert (
        package.get_resource("chunk2").stats["hash"]
        == "556e92cdacfc46c2338ab0b88daf9d560c6760eac2d4cb6f7df589c108fc07ce"
    )


def test_describe_package_expand():
    package = describe("data/chunk*.csv", expand=True)
    assert package.get_resource("chunk1").layout.header is True
    assert package.get_resource("chunk1").schema.missing_values == [""]
