import pytest

from frictionless import Detector, Dialect, formats, platform
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


def test_csv_parser():
    with TableResource(path="data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_with_bom():
    with TableResource(path="data/bom.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_with_bom_with_encoding():
    with TableResource(path="data/bom.csv", encoding="utf-8") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_excel():
    data = b"header1,header2\nvalue1,value2\nvalue3,value4"
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_excel_tab():
    data = b"header1\theader2\nvalue1\tvalue2\nvalue3\tvalue4"
    control = formats.CsvControl(delimiter="\t")
    with TableResource(data=data, format="csv", control=control) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_unix():
    data = b'"header1","header2"\n"value1","value2"\n"value3","value4"'
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_escaping():
    control = formats.CsvControl(escape_char="\\")
    with TableResource(path="data/escaping.csv", control=control) as resource:
        assert resource.header == ["ID", "Test"]
        assert resource.read_rows() == [
            {"ID": 1, "Test": "Test line 1"},
            {"ID": 2, "Test": 'Test " line 2'},
            {"ID": 3, "Test": 'Test " line 3'},
        ]


def test_csv_parser_doublequote():
    with TableResource(path="data/doublequote.csv") as resource:
        assert len(resource.header) == 17
        for row in resource.row_stream:
            assert len(row) == 17


def test_csv_parser_stream():
    data = open("data/table.csv", mode="rb")
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_csv_parser_buffer():
    data = "id,name\n1,english\n2,中国人\n".encode("utf-8")
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_csv_parser_remote():
    with TableResource(path=BASEURL % "data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_csv_parser_remote_non_ascii_url():
    path = "http://data.defra.gov.uk/ops/government_procurement_card/over_£500_GPC_apr_2013.csv"
    with TableResource(path=path) as resource:
        assert resource.header == [
            "Entity",
            "Transaction Posting Date",
            "Merchant Name",
            "Amount",
            "Description",
        ]


def test_csv_parser_delimiter():
    data = b'"header1";"header2"\n"value1";"value2"\n"value3";"value4"'
    control = formats.CsvControl(delimiter=";")
    with TableResource(data=data, format="csv", control=control) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_escapechar():
    data = b"header1%,header2\nvalue1%,value2\nvalue3%,value4"
    control = formats.CsvControl(escape_char="%")
    with TableResource(data=data, format="csv", control=control) as resource:
        assert resource.header == ["header1,header2"]
        assert resource.read_rows() == [
            {"header1,header2": "value1,value2"},
            {"header1,header2": "value3,value4"},
        ]


def test_csv_parser_quotechar():
    data = b"%header1,header2%\n%value1,value2%\n%value3,value4%"
    control = formats.CsvControl(quote_char="%")
    with TableResource(data=data, format="csv", control=control) as resource:
        assert resource.header == ["header1,header2"]
        assert resource.read_rows() == [
            {"header1,header2": "value1,value2"},
            {"header1,header2": "value3,value4"},
        ]


def test_csv_parser_skipinitialspace():
    data = b"header1, header2\nvalue1, value2\nvalue3, value4"
    control = formats.CsvControl(skip_initial_space=False)
    with TableResource(data=data, format="csv", control=control) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": " value2"},
            {"header1": "value3", "header2": " value4"},
        ]


def test_csv_parser_skipinitialspace_default():
    data = b"header1, header2\nvalue1, value2\nvalue3, value4"
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


def test_csv_parser_detect_delimiter_tab():
    data = b"a1\tb1\tc1A,c1B\na2\tb2\tc2\n"
    dialect = Dialect(header=False)
    with TableResource(data=data, format="csv", dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": "a1", "field2": "b1", "field3": "c1A,c1B"},
            {"field1": "a2", "field2": "b2", "field3": "c2"},
        ]


def test_csv_parser_detect_delimiter_semicolon():
    data = b"a1;b1\na2;b2\n"
    dialect = Dialect(header=False)
    with TableResource(data=data, format="csv", dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": "a1", "field2": "b1"},
            {"field1": "a2", "field2": "b2"},
        ]


def test_csv_parser_detect_delimiter_pipe():
    data = b"a1|b1\na2|b2\n"
    dialect = Dialect(header=False)
    with TableResource(data=data, format="csv", dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": "a1", "field2": "b1"},
            {"field1": "a2", "field2": "b2"},
        ]


def test_csv_parser_dialect_should_not_persist_if_sniffing_fails_issue_goodtables_228():
    data1 = b"a;b;c\n#comment"
    data2 = b"a,b,c\n#comment"
    control = formats.CsvControl(delimiter=";")
    with TableResource(data=data1, format="csv", control=control) as resource:
        assert resource.header == ["a", "b", "c"]
    with TableResource(data=data2, format="csv") as resource:
        assert resource.header == ["a", "b", "c"]


def test_csv_parser_quotechar_is_empty_string():
    data = b'header1,header2",header3\nvalue1,value2",value3'
    control = formats.CsvControl(quote_char="")
    with TableResource(data=data, format="csv", control=control) as resource:
        assert resource.header == ["header1", 'header2"', "header3"]
        assert resource.read_rows() == [
            {"header1": "value1", 'header2"': 'value2"', "header3": "value3"},
        ]


def test_csv_parser_format_tsv():
    detector = Detector(schema_patch={"missingValues": ["\\N"]})
    with TableResource(path="data/table.tsv", detector=detector) as resource:
        assert resource.dialect.to_descriptor() == {"csv": {"delimiter": "\t"}}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
            {"id": 3, "name": None},
        ]


# Write


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.csv")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_write_delimiter(tmpdir):
    control = formats.CsvControl(delimiter=";")
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.csv")), control=control)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.dialect.to_descriptor() == {"csv": {"delimiter": ";"}}
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_write_inline_source(tmpdir):
    source = TableResource(data=[{"key1": "value1", "key2": "value2"}])
    target = TableResource(path=str(tmpdir.join("table.csv")))
    source.write(target)
    with target:
        assert target.header == ["key1", "key2"]
        assert target.read_rows() == [
            {"key1": "value1", "key2": "value2"},
        ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_tsv_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.tsv")))
    source.write(target)
    assert target.normpath
    with open(target.normpath, encoding="utf-8") as file:
        assert file.read() == "id\tname\n1\tenglish\n2\t中国人\n"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_write_newline_lf(tmpdir):
    control = formats.CsvControl(line_terminator="\n")
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.csv")), control=control)
    source.write(target)
    with target:
        assert target.dialect.to_descriptor() == {"csv": {"lineTerminator": "\n"}}
    assert target.normpath
    with open(target.normpath, "rb") as file:
        assert file.read().decode("utf-8") == "id,name\n1,english\n2,中国人\n"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_write_newline_crlf(tmpdir):
    control = formats.CsvControl(line_terminator="\r\n")
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.csv")), control=control)
    source.write(target)
    with target:
        assert target.dialect.to_descriptor() == {"csv": {"lineTerminator": "\r\n"}}
    assert target.normpath
    with open(target.normpath, "rb") as file:
        assert file.read().decode("utf-8") == "id,name\r\n1,english\r\n2,中国人\r\n"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_csv_parser_write_skip_header(tmpdir):
    data = b"header1,header2\nvalue11,value12\nvalue21,value22"
    path = str(tmpdir.join("table.csv"))
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        resource.write_table(path, dialect=Dialect(header=False))
    with open(path, "rb") as file:
        assert file.read() == b"value11,value12\r\nvalue21,value22\r\n"


# Bugs


def test_csv_parser_proper_quote_issue_493():
    resource = TableResource(path="data/issue-493.csv")
    resource.infer()
    assert resource.dialect.to_descriptor() == {}
    assert len(resource.schema.fields) == 126
