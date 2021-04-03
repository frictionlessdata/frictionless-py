from frictionless import Detector, Layout, describe, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


def test_describe_resource():
    resource = describe("data/table.csv")
    assert resource.metadata_valid
    assert resource == {
        "profile": "tabular-data-resource",
        "name": "table",
        "path": "data/table.csv",
        "scheme": "file",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }


def test_describe_resource_with_stats():
    resource = describe("data/table.csv", stats=True)
    assert resource.metadata_valid
    if IS_UNIX:
        assert resource == {
            "profile": "tabular-data-resource",
            "name": "table",
            "path": "data/table.csv",
            "scheme": "file",
            "format": "csv",
            "hashing": "md5",
            "encoding": "utf-8",
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
            "stats": {
                "hash": "6c2c61dd9b0e9c6876139a449ed87933",
                "bytes": 30,
                "fields": 2,
                "rows": 2,
            },
        }


def test_describe_resource_schema():
    resource = describe("data/table-infer.csv")
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_utf8():
    resource = describe("data/table-infer-utf8.csv")
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_expand():
    resource = describe("data/table-infer.csv", expand=True)
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer", "format": "default", "bareNumber": True},
            {"name": "age", "type": "integer", "format": "default", "bareNumber": True},
            {"name": "name", "type": "string", "format": "default"},
        ],
        "missingValues": [""],
    }


def test_describe_resource_schema_infer_volume():
    detector = Detector(sample_size=4)
    resource = describe("data/table-infer-row-limit.csv", detector=detector)
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_with_missing_values_default():
    resource = describe("data/table-infer-missing-values.csv")
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_with_missing_values_using_the_argument():
    detector = Detector(field_missing_values=["-"])
    resource = describe("data/table-infer-missing-values.csv", detector=detector)
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "missingValues": ["-"],
    }


def test_describe_resource_schema_check_type_boolean_string_tie():
    layout = Layout(header=False)
    detector = Detector(field_names=["field"])
    resource = describe([["f"], ["stringish"]], layout=layout, detector=detector)
    assert resource.schema.get_field("field").type == "string"


# Issues


def test_describe_resource_schema_xlsx_file_with_boolean_column_issue_203():
    resource = describe("data/table-infer-boolean.xlsx")
    assert resource.schema == {
        "fields": [
            {"name": "number", "type": "integer"},
            {"name": "string", "type": "string"},
            {"name": "boolean", "type": "boolean"},
        ],
    }


def test_describe_resource_schema_increase_limit_issue_212():
    detector = Detector(sample_size=200)
    resource = describe("data/table-infer-increase-limit.csv", detector=detector)
    assert resource.schema == {
        "fields": [{"name": "a", "type": "integer"}, {"name": "b", "type": "number"}],
    }


def test_describe_resource_values_with_leading_zeros_issue_492():
    resource = describe("data/leading-zeros.csv")
    assert resource.schema == {"fields": [{"name": "value", "type": "integer"}]}
    assert resource.read_rows() == [{"value": 1}, {"value": 2}, {"value": 3}]


def test_describe_schema_proper_quote_issue_493():
    resource = describe("data/issue-493.csv")
    assert resource.dialect.quote_char == '"'
    assert len(resource.schema.fields) == 126


def test_describe_file_with_different_characters_name_issue_600():
    assert describe("data/table_with_data.csv").name == "table_with_data"
    assert describe("data/Table With Data.csv").name == "table-with-data"
    assert describe("data/Таблица.csv").name == "tablitsa"


def test_describe_resource_compression_gzip_issue_606():
    resource = describe("data/table.csv.gz", stats=True)
    assert resource.name == "table"
    assert resource.stats["hash"] == "edf56ce48e402d83eb08d5dac6aa2ad9"
    assert resource.stats["bytes"] == 61
