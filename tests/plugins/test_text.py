from frictionless import Table


# Read


def test_table_text():
    source = "text://header1,header2\nvalue1,value2\nvalue3,value4"
    with Table(source, format="csv") as table:
        assert table.header == ["header1", "header2"]
        assert table.read_data() == [["value1", "value2"], ["value3", "value4"]]


def test_table_text_format_in_path():
    source = "text://header1,header2\nvalue1,value2\nvalue3,value4.csv"
    with Table(source) as table:
        assert table.header == ["header1", "header2"]
        assert table.read_data() == [["value1", "value2"], ["value3", "value4"]]
