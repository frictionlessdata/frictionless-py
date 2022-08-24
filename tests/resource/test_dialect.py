from frictionless import Resource, Dialect, Control, Schema, fields, formats


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource_dialect_header():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_header_false():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "without-headers.csv",
        "dialect": {"header": False},
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    print(resource.normpath)
    assert resource.dialect.header is False
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]


def test_resource_dialect_header_unicode():
    with Resource("data/table-unicode-headers.csv") as resource:
        assert resource.header == ["id", "国人"]
        assert resource.read_rows() == [
            {"id": 1, "国人": "english"},
            {"id": 2, "国人": "中国人"},
        ]


def test_resource_dialect_header_stream_context_manager():
    source = open("data/table.csv", mode="rb")
    with Resource(source, format="csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_header_inline():
    source = [[], ["id", "name"], ["1", "english"], ["2", "中国人"]]
    dialect = Dialect(header_rows=[2])
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_header_json_keyed():
    source = "[" '{"id": 1, "name": "english"},' '{"id": 2, "name": "中国人"}]'
    source = source.encode("utf-8")
    with Resource(source, type="table", format="json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_header_inline_keyed():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_header_inline_keyed_headers_is_none():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    dialect = Dialect(header=False)
    with Resource(source, dialect=dialect) as resource:
        assert resource.labels == []
        assert resource.header == ["field1", "field2"]
        assert resource.read_rows() == [
            {"field1": "id", "field2": "name"},
            {"field1": "1", "field2": "english"},
            {"field1": "2", "field2": "中国人"},
        ]


def test_resource_dialect_header_xlsx_multiline():
    source = "data/multiline-headers.xlsx"
    control = Control.from_descriptor({"type": "excel", "fillMergedCells": True})
    dialect = Dialect(header_rows=[1, 2, 3, 4, 5], controls=[control])
    with Resource(source, dialect=dialect) as resource:
        header = resource.header
        assert header == [
            "Region",
            "Caloric contribution (%)",
            "Cumulative impact of changes on cost of food basket from previous quarter",
            "Cumulative impact of changes on cost of food basket from baseline (%)",
        ]
        assert resource.read_rows() == [
            {header[0]: "A", header[1]: "B", header[2]: "C", header[3]: "D"},
        ]


def test_resource_dialect_header_csv_multiline_headers_join():
    source = b"k1\nk2\nv1\nv2\nv3"
    dialect = Dialect(header_rows=[1, 2], header_join=":")
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["k1:k2"]
        assert resource.read_rows() == [
            {"k1:k2": "v1"},
            {"k1:k2": "v2"},
            {"k1:k2": "v3"},
        ]


def test_resource_dialect_header_csv_multiline_headers_duplicates():
    source = b"k1\nk1\nv1\nv2\nv3"
    dialect = Dialect(header_rows=[1, 2])
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["k1"]
        assert resource.read_rows() == [
            {"k1": "v1"},
            {"k1": "v2"},
            {"k1": "v3"},
        ]


def test_resource_dialect_header_strip_and_non_strings():
    source = [[" header ", 2, 3, None], ["value1", "value2", "value3", "value4"]]
    dialect = Dialect(header_rows=[1])
    with Resource(source, dialect=dialect) as resource:
        assert resource.labels == ["header", "2", "3", ""]
        assert resource.header == ["header", "2", "3", "field4"]
        assert resource.read_rows() == [
            {"header": "value1", "2": "value2", "3": "value3", "field4": "value4"},
        ]


def test_resource_layout_header_case_default():
    schema = Schema(fields=[fields.AnyField(name="ID"), fields.AnyField(name="NAME")])
    with Resource("data/table.csv", schema=schema) as resource:
        assert resource.schema.field_names == ["ID", "NAME"]
        assert resource.labels == ["id", "name"]
        assert resource.header == ["ID", "NAME"]
        assert resource.header.valid is False
        assert resource.header.errors[0].type == "incorrect-label"
        assert resource.header.errors[1].type == "incorrect-label"


def test_resource_layout_header_case_is_false():
    dialect = Dialect(header_case=False)
    schema = Schema(fields=[fields.AnyField(name="ID"), fields.AnyField(name="NAME")])
    with Resource("data/table.csv", dialect=dialect, schema=schema) as resource:
        assert resource.schema.field_names == ["ID", "NAME"]
        assert resource.labels == ["id", "name"]
        assert resource.header == ["ID", "NAME"]
        assert resource.header.valid is True


def test_resource_dialect_skip_rows():
    source = "data/skip-rows.csv"
    dialect = Dialect(comment_char="#", comment_rows=[5])
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
        ]


def test_resource_dialect_skip_rows_with_headers():
    source = "data/skip-rows.csv"
    dialect = Dialect(comment_char="#")
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_skip_rows_with_headers_example_from_readme():
    dialect = Dialect(comment_char="#")
    source = [["#comment"], ["name", "order"], ["John", 1], ["Alex", 2]]
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["name", "order"]
        assert resource.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_resource_dialect_from_descriptor():
    dialect = {
        "delimiter": "|",
        "quoteChar": "#",
        "escapeChar": "-",
        "doubleQuote": False,
        "skipInitialSpace": False,
    }
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "dialect.csv",
        "schema": "resource-schema.json",
        "dialect": dialect,
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": " |##"},
    ]


def test_resource_dialect_csv_default():
    with Resource("data/table.csv") as resource:
        control = resource.dialect.get_control("csv")
        assert isinstance(control, formats.CsvControl)
        assert control.delimiter == ","
        assert control.line_terminator == "\r\n"
        assert control.double_quote is True
        assert control.quote_char == '"'
        assert control.skip_initial_space is False
        assert resource.header == ["id", "name"]
        assert resource.dialect.header is True
        assert resource.dialect.header_rows == [1]
        # TODO: review
        # All the values are default
        #  assert resource.dialect == {}
        #  assert resource.layout == {}
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_csv_delimiter():
    with Resource("data/delimiter.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.dialect.to_descriptor() == {"csv": {"delimiter": ";"}}
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_json_property():
    source = b'{"root": [["header1", "header2"], ["value1", "value2"]]}'
    dialect = Dialect.from_descriptor({"json": {"property": "root"}})
    with Resource(source, type="table", format="json", dialect=dialect) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
        ]


def test_resource_dialect_header_false_official():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "without-headers.csv",
        "dialect": {"header": False},
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]
