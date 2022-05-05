from frictionless import Package, Resource, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Infer


def test_package_infer():
    package = Package("data/infer/*.csv")
    package.infer(stats=True)
    assert package.metadata_valid
    if IS_UNIX:
        assert package == {
            "profile": "data-package",
            "resources": [
                {
                    "path": "data/infer/data.csv",
                    "profile": "tabular-data-resource",
                    "name": "data",
                    "scheme": "file",
                    "format": "csv",
                    "hashing": "md5",
                    "encoding": "utf-8",
                    "schema": {
                        "fields": [
                            {"name": "id", "type": "string"},
                            {"name": "name", "type": "string"},
                            {"name": "description", "type": "string"},
                            {"name": "amount", "type": "number"},
                        ]
                    },
                    "stats": {
                        "hash": "c028f525f314c49ea48ed09e82292ed2",
                        "bytes": 114,
                        "fields": 4,
                        "rows": 2,
                    },
                },
                {
                    "path": "data/infer/data2.csv",
                    "profile": "tabular-data-resource",
                    "name": "data2",
                    "scheme": "file",
                    "format": "csv",
                    "hashing": "md5",
                    "encoding": "utf-8",
                    "schema": {
                        "fields": [
                            {"name": "parent", "type": "string"},
                            {"name": "comment", "type": "string"},
                        ]
                    },
                    "stats": {
                        "hash": "cb4a683d8eecb72c9ac9beea91fd592e",
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
    assert package.metadata_valid
    assert len(package.resources) == 2
    assert package.resources[0].path == "data.csv"
    assert package.resources[1].path == "data2.csv"


def test_package_infer_multiple_paths():
    package = Package(["data.csv", "data2.csv"], basepath="data/infer")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 2
    assert package.resources[0].path == "data.csv"
    assert package.resources[1].path == "data2.csv"


def test_package_infer_non_utf8_file():
    package = Package("data/table-with-accents.csv")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 1
    assert package.resources[0].encoding == "iso8859-1"


def test_package_infer_empty_file():
    package = Package("data/empty.csv")
    package.infer()
    assert package.metadata_valid
    assert len(package.resources) == 1
    assert package.resources[0].stats["bytes"] == 0


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
