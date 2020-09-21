from frictionless import describe


# General


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
                "compression": "no",
                "compressionPath": "",
                "dialect": {},
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
                "hash": "8fff9d97e5c0cb77b7c469ec37c8e766",
                "bytes": 18,
                "rows": 1,
            },
            {
                "path": "data/chunk2.csv",
                "profile": "tabular-data-resource",
                "name": "chunk2",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "compression": "no",
                "compressionPath": "",
                "dialect": {},
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
                "hash": "ebfa07d04a148a92a18078f78468694d",
                "bytes": 20,
                "rows": 1,
            },
        ],
    }


def test_describe_package_expand():
    package = describe("data/chunk*.csv", expand=True)
    assert package.get_resource("chunk1").dialect.header is True
    assert package.get_resource("chunk1").schema.missing_values == [""]
