import pytest
from frictionless import Resource, Schema, Field, Layout, helpers
from frictionless import FrictionlessException
from frictionless.plugins.excel import ExcelDialect


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Layout


def test_resource_layout_header():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_header_false():
    layout = {"header": False}
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "without-headers.csv",
        "layout": layout,
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.layout == layout
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]


def test_resource_layout_header_unicode():
    with Resource("data/table-unicode-headers.csv") as resource:
        assert resource.header == ["id", "国人"]
        assert resource.read_rows() == [
            {"id": 1, "国人": "english"},
            {"id": 2, "国人": "中国人"},
        ]


def test_resource_layout_header_stream_context_manager():
    source = open("data/table.csv", mode="rb")
    with Resource(source, format="csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_header_inline():
    source = [[], ["id", "name"], ["1", "english"], ["2", "中国人"]]
    layout = Layout(header_rows=[2])
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_header_json_keyed():
    source = "[" '{"id": 1, "name": "english"},' '{"id": 2, "name": "中国人"}]'
    source = source.encode("utf-8")
    with Resource(source, format="json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_header_inline_keyed():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_header_inline_keyed_headers_is_none():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    layout = Layout(header=False)
    with Resource(source, layout=layout) as resource:
        assert resource.labels == []
        assert resource.header == ["field1", "field2"]
        assert resource.read_rows() == [
            {"field1": "id", "field2": "name"},
            {"field1": "1", "field2": "english"},
            {"field1": "2", "field2": "中国人"},
        ]


def test_resource_layout_header_xlsx_multiline():
    source = "data/multiline-headers.xlsx"
    dialect = ExcelDialect(fill_merged_cells=True)
    layout = Layout(header_rows=[1, 2, 3, 4, 5])
    with Resource(source, dialect=dialect, layout=layout) as resource:
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


def test_resource_layout_header_csv_multiline_headers_join():
    source = b"k1\nk2\nv1\nv2\nv3"
    layout = Layout(header_rows=[1, 2], header_join=":")
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["k1:k2"]
        assert resource.read_rows() == [
            {"k1:k2": "v1"},
            {"k1:k2": "v2"},
            {"k1:k2": "v3"},
        ]


def test_resource_layout_header_csv_multiline_headers_duplicates():
    source = b"k1\nk1\nv1\nv2\nv3"
    layout = Layout(header_rows=[1, 2])
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["k1"]
        assert resource.read_rows() == [
            {"k1": "v1"},
            {"k1": "v2"},
            {"k1": "v3"},
        ]


def test_resource_layout_header_strip_and_non_strings():
    source = [[" header ", 2, 3, None], ["value1", "value2", "value3", "value4"]]
    layout = Layout(header_rows=[1])
    with Resource(source, layout=layout) as resource:
        assert resource.labels == ["header", "2", "3", ""]
        assert resource.header == ["header", "2", "3", "field4"]
        assert resource.read_rows() == [
            {"header": "value1", "2": "value2", "3": "value3", "field4": "value4"},
        ]


def test_resource_layout_header_case_default():
    schema = Schema(fields=[Field(name="ID"), Field(name="NAME")])
    with Resource("data/table.csv", schema=schema) as resource:
        assert resource.schema.field_names == ["ID", "NAME"]
        assert resource.labels == ["id", "name"]
        assert resource.header == ["ID", "NAME"]
        assert resource.header.valid is False
        assert resource.header.errors[0].code == "incorrect-label"
        assert resource.header.errors[1].code == "incorrect-label"


def test_resource_layout_header_case_is_false():
    layout = Layout(header_case=False)
    schema = Schema(fields=[Field(name="ID"), Field(name="NAME")])
    with Resource("data/table.csv", layout=layout, schema=schema) as resource:
        assert resource.schema.field_names == ["ID", "NAME"]
        assert resource.labels == ["id", "name"]
        assert resource.header == ["ID", "NAME"]
        assert resource.header.valid is True


def test_resource_layout_pick_fields():
    layout = Layout(pick_fields=["header2"])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2"]
        assert resource.header.field_positions == [2]
        assert resource.read_rows() == [
            {"header2": "value2"},
        ]


def test_resource_layout_pick_fields_position():
    layout = Layout(pick_fields=[2])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2"]
        assert resource.header.field_positions == [2]
        assert resource.read_rows() == [
            {"header2": "value2"},
        ]


def test_resource_layout_pick_fields_regex():
    layout = Layout(pick_fields=["<regex>header(2)"])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2"]
        assert resource.header.field_positions == [2]
        assert resource.read_rows() == [
            {"header2": "value2"},
        ]


def test_resource_layout_pick_fields_position_and_prefix():
    layout = Layout(pick_fields=[2, "header3"])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2", "header3"]
        assert resource.header.field_positions == [2, 3]
        assert resource.read_rows() == [
            {"header2": "value2", "header3": "value3"},
        ]


def test_resource_layout_skip_fields():
    layout = Layout(skip_fields=["header2"])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header1", "header3"]
        assert resource.header.field_positions == [1, 3]
        assert resource.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_resource_layout_skip_fields_position():
    layout = Layout(skip_fields=[2])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header1", "header3"]
        assert resource.header.field_positions == [1, 3]
        assert resource.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_resource_layout_skip_fields_regex():
    layout = Layout(skip_fields=["<regex>header(1|3)"])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2"]
        assert resource.header.field_positions == [2]
        assert resource.read_rows() == [
            {"header2": "value2"},
        ]


def test_resource_layout_skip_fields_position_and_prefix():
    layout = Layout(skip_fields=[2, "header3"])
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header1"]
        assert resource.header.field_positions == [1]
        assert resource.read_rows() == [
            {"header1": "value1"},
        ]


def test_resource_layout_skip_fields_blank_header():
    layout = Layout(skip_fields=[""])
    source = b"header1,,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header1", "header3"]
        assert resource.header.field_positions == [1, 3]
        assert resource.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_resource_layout_skip_fields_blank_header_notation():
    layout = Layout(skip_fields=["<blank>"])
    source = b"header1,,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header1", "header3"]
        assert resource.header.field_positions == [1, 3]
        assert resource.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_resource_layout_skip_fields_keyed_source():
    source = [{"id": 1, "name": "london"}, {"id": 2, "name": "paris"}]
    with Resource(source, layout={"skipFields": ["id"]}) as resource:
        assert resource.header == ["name"]
        assert resource.read_rows() == [{"name": "london"}, {"name": "paris"}]
    with Resource(source, layout={"skipFields": [1]}) as resource:
        assert resource.header == ["name"]
        assert resource.read_rows() == [{"name": "london"}, {"name": "paris"}]
    with Resource(source, layout={"skipFields": ["name"]}) as resource:
        assert resource.header == ["id"]
        assert resource.read_rows() == [{"id": 1}, {"id": 2}]
    with Resource(source, layout={"skipFields": [2]}) as resource:
        assert resource.header == ["id"]
        assert resource.read_rows() == [{"id": 1}, {"id": 2}]


def test_resource_layout_limit_fields():
    layout = Layout(limit_fields=1)
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header1"]
        assert resource.header.field_positions == [1]
        assert resource.read_rows() == [
            {"header1": "value1"},
        ]


def test_resource_layout_offset_fields():
    layout = Layout(offset_fields=1)
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2", "header3"]
        assert resource.header.field_positions == [2, 3]
        assert resource.read_rows() == [
            {"header2": "value2", "header3": "value3"},
        ]


def test_resource_layout_limit_offset_fields():
    layout = Layout(limit_fields=1, offset_fields=1)
    source = b"header1,header2,header3\nvalue1,value2,value3"
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.header == ["header2"]
        assert resource.header.field_positions == [2]
        assert resource.read_rows() == [
            {"header2": "value2"},
        ]


def test_resource_layout_pick_rows():
    source = "data/skip-rows.csv"
    layout = Layout(header=False, pick_rows=["1", "2"])
    with Resource(source, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
        ]


def test_resource_layout_pick_rows_number():
    source = "data/skip-rows.csv"
    layout = Layout(header=False, pick_rows=[3, 5])
    with Resource(source, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
        ]


def test_resource_layout_pick_rows_regex():
    source = [
        ["# comment"],
        ["name", "order"],
        ["# cat"],
        ["# dog"],
        ["John", 1],
        ["Alex", 2],
    ]
    layout = Layout(pick_rows=[r"<regex>(name|John|Alex)"])
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["name", "order"]
        assert resource.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_resource_layout_skip_rows():
    source = "data/skip-rows.csv"
    layout = Layout(skip_rows=["#", 5])
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
        ]


def test_resource_layout_skip_rows_excel_empty_column():
    source = "data/skip-rows.xlsx"
    layout = Layout(skip_rows=[""])
    with Resource(source, layout=layout) as resource:
        assert resource.read_rows() == [
            {"Table 1": "A", "field2": "B"},
            {"Table 1": 8, "field2": 9},
        ]


def test_resource_layout_skip_rows_with_headers():
    source = "data/skip-rows.csv"
    layout = Layout(skip_rows=["#"])
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_layout_skip_rows_with_headers_example_from_readme():
    layout = Layout(skip_rows=["#"])
    source = [["#comment"], ["name", "order"], ["John", 1], ["Alex", 2]]
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["name", "order"]
        assert resource.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_resource_layout_skip_rows_regex():
    source = [
        ["# comment"],
        ["name", "order"],
        ["# cat"],
        ["# dog"],
        ["John", 1],
        ["Alex", 2],
    ]
    layout = Layout(skip_rows=["# comment", r"<regex># (cat|dog)"])
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["name", "order"]
        assert resource.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_resource_layout_skip_rows_preset():
    source = [
        ["name", "order"],
        ["", ""],
        [],
        ["Ray", 0],
        ["John", 1],
        ["Alex", 2],
        ["", 3],
        [None, 4],
        ["", None],
    ]
    layout = Layout(skip_rows=["<blank>"])
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["name", "order"]
        assert resource.read_rows() == [
            {"name": "Ray", "order": 0},
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
            {"name": None, "order": 3},
            {"name": None, "order": 4},
        ]


def test_resource_layout_limit_rows():
    source = "data/long.csv"
    layout = Layout(limit_rows=1)
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "a"},
        ]


def test_resource_layout_offset_rows():
    source = "data/long.csv"
    layout = Layout(offset_rows=5)
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 6, "name": "f"},
        ]


def test_resource_layout_limit_offset_rows():
    source = "data/long.csv"
    layout = Layout(limit_rows=2, offset_rows=2)
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 3, "name": "c"},
            {"id": 4, "name": "d"},
        ]


def test_resource_layout_limit_fields_error_zero_issue_521():
    source = "data/long.csv"
    layout = Layout(limit_fields=0)
    resource = Resource(source, layout=layout)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "layout-error"
    assert error.note.count('minimum of 1" at "limitFields')


def test_resource_layout_offset_fields_error_zero_issue_521():
    source = "data/long.csv"
    layout = Layout(offset_fields=0)
    resource = Resource(source, layout=layout)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "layout-error"
    assert error.note.count('minimum of 1" at "offsetFields')


def test_resource_layout_limit_rows_error_zero_issue_521():
    source = "data/long.csv"
    layout = Layout(limit_rows=0)
    resource = Resource(source, layout=layout)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "layout-error"
    assert error.note.count('minimum of 1" at "limitRows')


def test_resource_layout_offset_rows_error_zero_issue_521():
    source = "data/long.csv"
    layout = Layout(offset_rows=0)
    resource = Resource(source, layout=layout)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "layout-error"
    assert error.note.count('minimum of 1" at "offsetRows')


def test_resource_layout_respect_set_after_creation_issue_503():
    resource = Resource(path="data/table.csv")
    resource.layout = Layout(limit_rows=1)
    assert resource.read_rows() == [{"id": 1, "name": "english"}]
    assert resource.header == ["id", "name"]
