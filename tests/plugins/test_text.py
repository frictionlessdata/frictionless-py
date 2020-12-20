from frictionless import Table


# Read


def test_text_loader():
    source = "text://header1,header2\nvalue1,value2\nvalue3,value4"
    with Table(source, format="csv") as table:
        assert table.header == ["header1", "header2"]
        assert table.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_text_loader_format_in_path():
    source = "text://header1,header2\nvalue1,value2\nvalue3,value4.csv"
    with Table(source) as table:
        assert table.header == ["header1", "header2"]
        assert table.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


# Write


def test_text_loader_write():
    source = "data/table.csv"
    with Table(source) as table:
        text = table.write(scheme="text", format="csv")
    assert text == "id,name\r\n1,english\r\n2,中国人\r\n"
