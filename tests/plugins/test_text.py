from frictionless import Resource


# Read


def test_text_loader():
    source = "text://header1,header2\nvalue1,value2\nvalue3,value4"
    with Resource(source, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_text_loader_format_in_path():
    source = "text://header1,header2\nvalue1,value2\nvalue3,value4.csv"
    with Resource(source) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


# Write


def test_text_loader_write():
    source = Resource("data/table.csv")
    target = source.write(Resource(scheme="text", format="csv"))
    assert target.path == "id,name\r\n1,english\r\n2,中国人\r\n"
