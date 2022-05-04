import pytest
from frictionless import Resource, Layout, Detector
from frictionless.plugins.csv import CsvDialect


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_csv_parser():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_with_bom():
    with Resource("data/bom.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_with_bom_with_encoding():
    with Resource("data/bom.csv", encoding="utf-8") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_excel():
    source = b"header1,header2\nvalue1,value2\nvalue3,value4"
    with Resource(source, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_excel_tab():
    source = b"header1\theader2\nvalue1\tvalue2\nvalue3\tvalue4"
    dialect = CsvDialect(delimiter="\t")
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_unix():
    source = b'"header1","header2"\n"value1","value2"\n"value3","value4"'
    with Resource(source, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_escaping():
    dialect = CsvDialect(escape_char="\\")
    with Resource("data/escaping.csv", dialect=dialect) as resource:
        assert resource.header == ["ID", "Test"]
        assert resource.read_rows() == [
            {"ID": 1, "Test": "Test line 1"},
            {"ID": 2, "Test": 'Test " line 2'},
            {"ID": 3, "Test": 'Test " line 3'},
        ]


def test_csv_parser_doublequote():
    with Resource("data/doublequote.csv") as resource:
        assert len(resource.header) == 17
        for row in resource:
            assert len(row) == 17


def test_csv_parser_stream():
    source = open("data/table.csv", mode="rb")
    with Resource(source, format="csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_buffer():
    source = "id,name\n1,english\n2,中国人\n".encode("utf-8")
    with Resource(source, format="csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_csv_parser_remote():
    with Resource(BASEURL % "data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_csv_parser_remote_non_ascii_url():
    source = "http://data.defra.gov.uk/ops/government_procurement_card/over_£500_GPC_apr_2013.csv"
    with Resource(source) as resource:
        assert resource.header == [
            "Entity",
            "Transaction Posting Date",
            "Merchant Name",
            "Amount",
            "Description",
        ]


def test_csv_parser_delimiter():
    source = b'"header1";"header2"\n"value1";"value2"\n"value3";"value4"'
    dialect = CsvDialect(delimiter=";")
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_escapechar():
    source = b"header1%,header2\nvalue1%,value2\nvalue3%,value4"
    dialect = CsvDialect(escape_char="%")
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["header1,header2"]
        assert resource.read_rows() == [
            {"header1,header2": "value1,value2"},
            {"header1,header2": "value3,value4"},
        ]


def test_csv_parser_quotechar():
    source = b"%header1,header2%\n%value1,value2%\n%value3,value4%"
    dialect = CsvDialect(quote_char="%")
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["header1,header2"]
        assert resource.read_rows() == [
            {"header1,header2": "value1,value2"},
            {"header1,header2": "value3,value4"},
        ]


def test_csv_parser_skipinitialspace():
    source = b"header1, header2\nvalue1, value2\nvalue3, value4"
    dialect = CsvDialect(skip_initial_space=False)
    with Resource(source, format="csv", dialect=dialect) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": " value2"},
            {"header1": "value3", "header2": " value4"},
        ]


def test_csv_parser_skipinitialspace_default():
    source = b"header1, header2\nvalue1, value2\nvalue3, value4"
    with Resource(source, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_detect_delimiter_tab():
    source = b"a1\tb1\tc1A,c1B\na2\tb2\tc2\n"
    layout = Layout(header=False)
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "a1", "field2": "b1", "field3": "c1A,c1B"},
            {"field1": "a2", "field2": "b2", "field3": "c2"},
        ]


def test_csv_parser_detect_delimiter_semicolon():
    source = b"a1;b1\na2;b2\n"
    layout = Layout(header=False)
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "a1", "field2": "b1"},
            {"field1": "a2", "field2": "b2"},
        ]


def test_csv_parser_detect_delimiter_pipe():
    source = b"a1|b1\na2|b2\n"
    layout = Layout(header=False)
    with Resource(source, format="csv", layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "a1", "field2": "b1"},
            {"field1": "a2", "field2": "b2"},
        ]


def test_csv_parser_dialect_should_not_persist_if_sniffing_fails_issue_goodtables_228():
    source1 = b"a;b;c\n#comment"
    source2 = b"a,b,c\n#comment"
    dialect = CsvDialect(delimiter=";")
    with Resource(source1, format="csv", dialect=dialect) as resource:
        assert resource.header == ["a", "b", "c"]
    with Resource(source2, format="csv") as resource:
        assert resource.header == ["a", "b", "c"]


def test_csv_parser_quotechar_is_empty_string():
    source = b'header1,header2",header3\nvalue1,value2",value3'
    dialect = CsvDialect(quote_char="")
    with Resource(source, format="csv", dialect=dialect) as resource:
        resource.header == ["header1", 'header2"', "header3"]
        assert resource.read_rows() == [
            {"header1": "value1", 'header2"': 'value2"', "header3": "value3"},
        ]


def test_csv_parser_format_tsv():
    detector = Detector(schema_patch={"missingValues": ["\\N"]})
    with Resource("data/table.tsv", detector=detector) as resource:
        assert resource.dialect == {"delimiter": "\t"}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
            {"id": 3, "name": None},
        ]


def test_csv_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.csv")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_write_delimiter(tmpdir):
    dialect = CsvDialect(delimiter=";")
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.csv")), dialect=dialect)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.dialect == {"delimiter": ";"}
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_write_inline_source(tmpdir):
    source = Resource([{"key1": "value1", "key2": "value2"}])
    target = Resource(str(tmpdir.join("table.csv")))
    source.write(target)
    with target:
        assert target.header == ["key1", "key2"]
        assert target.read_rows() == [
            {"key1": "value1", "key2": "value2"},
        ]


def test_csv_parser_tsv_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.tsv")))
    source.write(target)
    with open(target.fullpath, encoding="utf-8") as file:
        assert file.read() == "id\tname\n1\tenglish\n2\t中国人\n"


def test_csv_parser_write_newline_lf(tmpdir):
    dialect = CsvDialect(line_terminator="\n")
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.csv")), dialect=dialect)
    source.write(target)
    with target:
        assert target.dialect == {"lineTerminator": "\n"}
    with open(target.fullpath, "rb") as file:
        assert file.read().decode("utf-8") == "id,name\n1,english\n2,中国人\n"


def test_csv_parser_write_newline_crlf(tmpdir):
    dialect = CsvDialect(line_terminator="\r\n")
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.csv")), dialect=dialect)
    source.write(target)
    with target:
        assert target.dialect == {"lineTerminator": "\r\n"}
    with open(target.fullpath, "rb") as file:
        assert file.read().decode("utf-8") == "id,name\r\n1,english\r\n2,中国人\r\n"
