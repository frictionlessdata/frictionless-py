from frictionless import describe, Resource, Package, dialects


# General


def test_describe():
    resource = describe("data/table.csv")
    assert resource.metadata_valid
    assert resource == {
        "name": "table",
        "path": "data/table.csv",
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
        "profile": "tabular-data-resource",
        "hash": "6c2c61dd9b0e9c6876139a449ed87933",
        "bytes": 30,
        "rows": 2,
    }


def test_describe_resource():
    resource = describe("data/table.csv")
    assert isinstance(resource, Resource)


def test_describe_package():
    resource = describe(["data/table.csv"])
    assert isinstance(resource, Package)


def test_describe_package_pattern():
    resource = describe("data/chunk*.csv")
    assert isinstance(resource, Package)


def test_describe_package_source_type():
    resource = describe("data/table.csv", source_type="package")
    assert isinstance(resource, Package)


# Issues


def test_describe_blank_cells_issue_7():
    source = "header1,header2\n1,\n2,\n3,\n"
    resource = describe(source, scheme="text", format="csv")
    assert resource.schema == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "any"},
        ]
    }


def test_describe_whitespace_cells_issue_7():
    source = "header1,header2\n1, \n2, \n3, \n"
    resource = describe(source, scheme="text", format="csv")
    assert resource.schema == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "string"},
        ]
    }


def test_describe_whitespace_cells_with_skip_initial_space_issue_7():
    source = "header1,header2\n1, \n2, \n3, \n"
    dialect = dialects.CsvDialect(skip_initial_space=True)
    resource = describe(source, scheme="text", format="csv", dialect=dialect)
    assert resource.schema == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "any"},
        ]
    }
