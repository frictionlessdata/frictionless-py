import pytest
from frictionless import Package, Dialect, describe, platform


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_describe_package():
    package = describe("data/tables/chunk*.csv")
    assert isinstance(package, Package)
    assert package.to_descriptor() == {
        "resources": [
            {
                "path": "data/tables/chunk1.csv",
                "name": "chunk1",
                "type": "table",
                "scheme": "file",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
            },
            {
                "name": "chunk2",
                "path": "data/tables/chunk2.csv",
                "type": "table",
                "scheme": "file",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
            },
        ],
    }


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_describe_package_with_stats():
    package = describe("data/tables/chunk*.csv", stats=True)
    assert isinstance(package, Package)
    assert package.to_descriptor() == {
        "resources": [
            {
                "path": "data/tables/chunk1.csv",
                "name": "chunk1",
                "type": "table",
                "scheme": "file",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
                "stats": {
                    "md5": "8fff9d97e5c0cb77b7c469ec37c8e766",
                    "sha256": "3872c98bd72eb4a91ac666f7758cd83da904c61a35178ca1ce9e10d6b009cd21",
                    "bytes": 18,
                    "fields": 2,
                    "rows": 1,
                },
            },
            {
                "name": "chunk2",
                "path": "data/tables/chunk2.csv",
                "type": "table",
                "scheme": "file",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
                "stats": {
                    "md5": "ebfa07d04a148a92a18078f78468694d",
                    "sha256": "556e92cdacfc46c2338ab0b88daf9d560c6760eac2d4cb6f7df589c108fc07ce",
                    "bytes": 20,
                    "fields": 2,
                    "rows": 1,
                },
            },
        ],
    }


def test_describe_package_basepath():
    package = describe("chunk*.csv", basepath="data")
    assert isinstance(package, Package)
    assert package.get_resource("chunk1").path == "chunk1.csv"
    assert package.get_resource("chunk2").path == "chunk2.csv"
    assert package.get_resource("chunk1").basepath == "data"
    assert package.get_resource("chunk2").basepath == "data"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_describe_package_hashing():
    package = describe("data/chunk*.csv", stats=True)
    assert isinstance(package, Package)
    assert (
        package.get_resource("chunk1").stats.sha256
        == "3872c98bd72eb4a91ac666f7758cd83da904c61a35178ca1ce9e10d6b009cd21"
    )
    assert (
        package.get_resource("chunk2").stats.sha256
        == "556e92cdacfc46c2338ab0b88daf9d560c6760eac2d4cb6f7df589c108fc07ce"
    )


# Bugs


def test_describe_package_with_dialect_1126():
    dialect = Dialect.from_descriptor({"csv": {"delimiter": ";"}})
    package = describe("data/country-2.csv", type="package", dialect=dialect)
    assert isinstance(package, Package)
    assert package.get_resource("country-2").schema.to_descriptor() == {
        "fields": [
            {"type": "integer", "name": "id"},
            {"type": "integer", "name": "neighbor_id"},
            {"type": "string", "name": "name"},
            {"type": "integer", "name": "population"},
        ]
    }


def test_describe_package_with_dialect_path_1126():
    package = describe("data/country-2.csv", type="package", dialect="data/dialect.json")
    assert isinstance(package, Package)
    assert package.get_resource("country-2").schema.to_descriptor() == {
        "fields": [
            {"type": "integer", "name": "id"},
            {"type": "integer", "name": "neighbor_id"},
            {"type": "string", "name": "name"},
            {"type": "integer", "name": "population"},
        ]
    }


def test_describe_package_with_incorrect_dialect_1126():
    dialect = Dialect.from_descriptor({"csv": {"delimiter": ","}})
    package = describe("data/country-2.csv", type="package", dialect=dialect)
    assert isinstance(package, Package)
    assert package.get_resource("country-2").schema.to_descriptor() == {
        "fields": [{"type": "string", "name": "# Author: the scientist"}]
    }


def test_describe_package_with_glob_having_one_incorrect_dialect_1126():
    dialect = Dialect.from_descriptor({"csv": {"delimiter": ","}})
    package = describe("data/country-*.csv", type="package", dialect=dialect)
    assert isinstance(package, Package)
    assert package.get_resource("country-1").schema.to_descriptor() == {
        "fields": [
            {"type": "integer", "name": "id"},
            {"type": "integer", "name": "neighbor_id"},
            {"type": "string", "name": "name"},
            {"type": "integer", "name": "population"},
        ]
    }
    assert package.get_resource("country-2").schema.to_descriptor() == {
        "fields": [{"type": "string", "name": "# Author: the scientist"}]
    }
