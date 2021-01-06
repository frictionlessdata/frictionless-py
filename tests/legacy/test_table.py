import io
import sys
import pytest
from frictionless import FrictionlessException
from frictionless import Table, Query, Schema, Field, Control, Dialect, helpers
from frictionless.plugins.remote import RemoteControl
from frictionless.plugins.excel import ExcelDialect
from frictionless.plugins.json import JsonDialect


# General


BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/%s"


def test_table():
    with Table("data/table.csv") as table:
        assert table.path == "data/table.csv"
        assert table.source == "data/table.csv"
        assert table.scheme == "file"
        assert table.format == "csv"
        assert table.encoding == "utf-8"
        assert table.innerpath == ""
        assert table.compression == ""
        assert table.header.row_positions == [1]
        assert table.header == ["id", "name"]
        assert table.sample == [["1", "english"], ["2", "中国人"]]
        assert table.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_read_rows():
    with Table("data/table.csv") as table:
        headers = table.header
        row1, row2 = table.read_rows()
        assert headers == ["id", "name"]
        assert headers.field_positions == [1, 2]
        assert headers.errors == []
        assert headers.valid is True
        assert row1.to_dict() == {"id": 1, "name": "english"}
        assert row1.field_positions == [1, 2]
        assert row1.row_position == 2
        assert row1.row_number == 1
        assert row1.errors == []
        assert row1.valid is True
        assert row2.to_dict() == {"id": 2, "name": "中国人"}
        assert row2.field_positions == [1, 2]
        assert row2.row_position == 3
        assert row2.row_number == 2
        assert row2.errors == []
        assert row2.valid is True


def test_table_row_stream():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert list(table.row_stream) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
        assert list(table.row_stream) == []


def test_table_row_stream_iterate():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        for row in table.row_stream:
            assert len(row) == 2
            assert row.row_number in [1, 2]
            if row.row_number == 1:
                assert row.to_dict() == {"id": 1, "name": "english"}
            if row.row_number == 2:
                assert row.to_dict() == {"id": 2, "name": "中国人"}


def test_table_row_stream_error_cells():
    with Table("data/table.csv", infer_type="integer") as table:
        row1, row2 = table.read_rows()
        assert table.header == ["id", "name"]
        assert row1.errors[0].code == "type-error"
        assert row1.error_cells == {"name": "english"}
        assert row1.to_dict() == {"id": 1, "name": None}
        assert row1.valid is False
        assert row2.errors[0].code == "type-error"
        assert row2.error_cells == {"name": "中国人"}
        assert row2.to_dict() == {"id": 2, "name": None}
        assert row2.valid is False


def test_table_row_stream_blank_cells():
    patch_schema = {"missingValues": ["1", "2"]}
    with Table("data/table.csv", patch_schema=patch_schema) as table:
        row1, row2 = table.read_rows()
        assert table.header == ["id", "name"]
        assert row1.blank_cells == {"id": "1"}
        assert row1.to_dict() == {"id": None, "name": "english"}
        assert row1.valid is True
        assert row2.blank_cells == {"id": "2"}
        assert row2.to_dict() == {"id": None, "name": "中国人"}
        assert row2.valid is True


def test_table_read_data():
    with Table("data/table.csv") as table:
        assert table.read_data() == [
            ["id", "name"],
            ["1", "english"],
            ["2", "中国人"],
        ]


def test_table_data_stream():
    with Table("data/table.csv") as table:
        assert list(table.data_stream) == [
            ["id", "name"],
            ["1", "english"],
            ["2", "中国人"],
        ]
        assert list(table.data_stream) == []


def test_table_data_stream_iterate():
    with Table("data/table.csv") as table:
        for number, cells in enumerate(table.data_stream):
            assert len(cells) == 2
            if number == 0:
                assert cells == ["id", "name"]
            if number == 1:
                assert cells == ["1", "english"]
            if number == 2:
                assert cells == ["2", "中国人"]


def test_table_empty():
    with Table("data/empty.csv") as table:
        assert table.header.missing
        assert table.header == []
        assert table.schema == {}
        assert table.read_rows() == []


def test_table_without_rows():
    with Table("data/without-rows.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == []
        assert table.schema == {
            "fields": [
                {"name": "id", "type": "any"},
                {"name": "name", "type": "any"},
            ]
        }


def test_table_without_headers():
    with Table("data/without-headers.csv") as table:
        assert table.header.missing
        assert table.header == []
        assert table.schema == {
            "fields": [
                {"name": "field1", "type": "integer"},
                {"name": "field2", "type": "string"},
            ]
        }
        assert table.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
            {"field1": 3, "field2": "german"},
        ]


def test_table_error_read_closed():
    table = Table("data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        table.read_rows()
    error = excinfo.value.error
    assert error.code == "error"
    assert error.note == 'the table has not been opened by "table.open()"'


def test_table_source_error_data():
    table = Table("[1,2]", scheme="text", format="json")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "source-error"
    assert error.note == "unsupported inline data"


# Scheme


def test_table_scheme_file():
    with Table("data/table.csv") as table:
        assert table.scheme == "file"


@pytest.mark.vcr
def test_table_scheme_https():
    with Table(BASE_URL % "data/table.csv") as table:
        assert table.scheme == "https"


def test_table_scheme_filelike():
    with Table(open("data/table.csv", mode="rb"), format="csv") as table:
        assert table.scheme == "filelike"


def test_table_scheme_text():
    with Table("text://a\nb", format="csv") as table:
        assert table.scheme == "text"


def test_table_scheme_error_bad_scheme():
    table = Table("", scheme="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == 'cannot create loader "bad". Try installing "frictionless-bad"'


def test_table_scheme_error_bad_scheme_and_format():
    table = Table("bad://bad.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == 'cannot create loader "bad". Try installing "frictionless-bad"'


def test_table_scheme_error_file_not_found():
    table = Table("bad.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad.csv'"


@pytest.mark.vcr
def test_table_scheme_error_file_not_found_remote():
    table = Table("https://example.com/bad.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note[18:] == "Not Found for url: https://example.com/bad.csv"


def test_table_scheme_error_file_not_found_bad_format():
    table = Table("bad.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad.bad'"


def test_table_scheme_error_file_not_found_bad_compression():
    table = Table("bad.csv", compression="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad.csv'"


# Format


def test_table_format_csv():
    with Table("data/table.csv") as table:
        assert table.format == "csv"


def test_table_format_ndjson():
    with Table("data/table.ndjson") as table:
        assert table.format == "ndjson"


def test_table_format_tsv():
    with Table("data/table.tsv") as table:
        assert table.format == "tsv"


def test_table_format_xls():
    with Table("data/table.xls") as table:
        assert table.format == "xls"


def test_table_format_xlsx():
    with Table("data/table.xlsx") as table:
        assert table.format == "xlsx"


def test_table_format_error_bad_format():
    table = Table("data/table.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'cannot create parser "bad". Try installing "frictionless-bad"'


def test_table_format_error_non_matching_format():
    table = Table("data/table.csv", format="xlsx")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'invalid excel file "data/table.csv"'


# Hashing


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_hashing():
    with Table("data/table.csv") as table:
        table.read_rows()
        assert table.hashing == "md5"
        assert table.stats["hash"] == "6c2c61dd9b0e9c6876139a449ed87933"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_hashing_provided():
    with Table("data/table.csv", hashing="sha1") as table:
        table.read_rows()
        assert table.hashing == "sha1"
        assert table.stats["hash"] == "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"


def test_table_hashing_error_bad_hashing():
    table = Table("data/table.csv", hashing="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "hashing-error"
    assert error.note == "unsupported hash type bad"


# Encoding


def test_table_encoding():
    with Table("data/table.csv") as table:
        assert table.encoding == "utf-8"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_encoding_explicit_utf8():
    with Table("data/table.csv", encoding="utf-8") as table:
        assert table.encoding == "utf-8"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_encoding_explicit_latin1():
    with Table("data/latin1.csv", encoding="latin1") as table:
        assert table.encoding == "iso8859-1"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "©"},
        ]


def test_table_encoding_utf_16():
    # Bytes encoded as UTF-16 with BOM in platform order is detected
    bio = io.BytesIO(u"en,English\nja,日本語".encode("utf-16"))
    with Table(bio, format="csv", headers=False) as table:
        assert table.encoding == "utf-16"
        assert table.read_rows() == [
            {"field1": "en", "field2": "English"},
            {"field1": "ja", "field2": "日本語"},
        ]


def test_table_encoding_error_bad_encoding():
    table = Table("data/table.csv", encoding="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "encoding-error"
    assert error.note == "unknown encoding: bad"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_encoding_error_non_matching_encoding():
    table = Table("data/table.csv", encoding="ascii")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "encoding-error"
    assert error.note[:51] == "'ascii' codec can't decode byte 0xe4 in position 20"


# Compression


def test_table_compression_local_csv_zip():
    with Table("data/table.csv.zip") as table:
        assert table.innerpath == "table.csv"
        assert table.compression == "zip"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_compression_local_csv_zip_multiple_files():
    with Table("data/table-multiple-files.zip", format="csv") as table:
        assert table.innerpath == "table-reverse.csv"
        assert table.compression == "zip"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "中国人"},
            {"id": 2, "name": "english"},
        ]


def test_table_compression_local_csv_zip_multiple_files_innerpath():
    with Table("data/table-multiple-files.zip", innerpath="table.csv") as table:
        assert table.innerpath == "table.csv"
        assert table.compression == "zip"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_compression_local_csv_zip_multiple_open():
    table = Table("data/table.csv.zip")

    # Open first time
    table.open()
    assert table.header == ["id", "name"]
    assert table.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    table.close()

    # Open second time
    table.open()
    assert table.header == ["id", "name"]
    assert table.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    table.close()


def test_table_compression_local_csv_gz():
    with Table("data/table.csv.gz") as table:
        assert table.innerpath == ""
        assert table.compression == "gz"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_compression_filelike_csv_zip():
    with open("data/table.csv.zip", "rb") as file:
        with Table(file, format="csv", compression="zip") as table:
            assert table.header == ["id", "name"]
            assert table.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


def test_table_compression_filelike_csv_gz():
    with open("data/table.csv.gz", "rb") as file:
        with Table(file, format="csv", compression="gz") as table:
            assert table.header == ["id", "name"]
            assert table.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


@pytest.mark.vcr
def test_table_compression_remote_csv_zip():
    source = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/data/table.csv.zip"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_table_compression_remote_csv_gz():
    source = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/data/table.csv.gz"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_compression_error_bad():
    table = Table("data/table.csv", compression="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "compression-error"
    assert error.note == 'compression "bad" is not supported'


def test_table_compression_error_invalid_zip():
    source = "id,filename\n1,archive.zip"
    table = Table(source, scheme="text", format="csv")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "compression-error"
    assert error.note == "File is not a zip file"


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python3.8+")
def test_table_compression_error_invalid_gz():
    source = "id,filename\n\1,dump.tar.gz"
    table = Table(source, scheme="text", format="csv")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "compression-error"
    assert error.note == "Not a gzipped file (b'id')"


# Control


def test_table_control():
    control = Control(detect_encoding=lambda sample: "utf-8")
    with Table("data/table.csv", control=control) as table:
        assert table.encoding == "utf-8"
        assert table.header == ["id", "name"]
        assert table.sample == [["1", "english"], ["2", "中国人"]]


@pytest.mark.vcr
def test_table_control_http_preload():
    control = RemoteControl(http_preload=True)
    with Table(BASE_URL % "data/table.csv", control=control) as table:
        assert table.header == ["id", "name"]
        assert table.sample == [["1", "english"], ["2", "中国人"]]
        assert table.control == {"newline": "", "httpPreload": True}


def test_table_control_bad_property():
    table = Table("data/table.csv", control={"bad": True})
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "control-error"
    assert error.note.count("bad")


# Dialect


def test_table_dialect():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.dialect.delimiter == ","
        assert table.dialect.line_terminator == "\r\n"
        assert table.dialect.double_quote is True
        assert table.dialect.quote_char == '"'
        assert table.dialect.skip_initial_space is False
        assert table.dialect.header is True
        assert table.dialect.header_rows == [1]
        # All the values are default
        assert table.dialect == {}
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_dialect_csv_delimiter():
    with Table("data/delimiter.csv") as table:
        assert table.header == ["id", "name"]
        assert table.dialect == {"delimiter": ";"}
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_dialect_json_property():
    source = '{"root": [["header1", "header2"], ["value1", "value2"]]}'
    dialect = JsonDialect(property="root")
    with Table(source, scheme="text", format="json", dialect=dialect) as table:
        assert table.header == ["header1", "header2"]
        assert table.read_rows() == [
            {"header1": "value1", "header2": "value2"},
        ]


def test_table_dialect_bad_property():
    table = Table("data/table.csv", dialect={"bad": True})
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "dialect-error"
    assert error.note.count("bad")


def test_table_dialect_header_case_default():
    schema = Schema(fields=[Field(name="ID"), Field(name="NAME")])
    with Table("data/table.csv", schema=schema) as table:
        assert table.schema.field_names == ["ID", "NAME"]
        assert table.header == ["id", "name"]
        assert table.header.valid is False
        assert table.header.errors[0].code == "incorrect-label"
        assert table.header.errors[1].code == "incorrect-label"


def test_table_dialect_header_case_is_false():
    dialect = Dialect(header_case=False)
    schema = Schema(fields=[Field(name="ID"), Field(name="NAME")])
    with Table("data/table.csv", dialect=dialect, schema=schema) as table:
        assert table.schema.field_names == ["ID", "NAME"]
        assert table.header == ["id", "name"]
        assert table.header.valid is True


# Query


def test_table_pick_fields():
    query = Query(pick_fields=["header2"])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2"]
        assert table.header.field_positions == [2]
        assert table.read_rows() == [
            {"header2": "value2"},
        ]


def test_table_pick_fields_position():
    query = Query(pick_fields=[2])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2"]
        assert table.header.field_positions == [2]
        assert table.read_rows() == [
            {"header2": "value2"},
        ]


def test_table_pick_fields_regex():
    query = Query(pick_fields=["<regex>header(2)"])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2"]
        assert table.header.field_positions == [2]
        assert table.read_rows() == [
            {"header2": "value2"},
        ]


def test_table_pick_fields_position_and_prefix():
    query = Query(pick_fields=[2, "header3"])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2", "header3"]
        assert table.header.field_positions == [2, 3]
        assert table.read_rows() == [
            {"header2": "value2", "header3": "value3"},
        ]


def test_table_skip_fields():
    query = Query(skip_fields=["header2"])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header1", "header3"]
        assert table.header.field_positions == [1, 3]
        assert table.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_table_skip_fields_position():
    query = Query(skip_fields=[2])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header1", "header3"]
        assert table.header.field_positions == [1, 3]
        assert table.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_table_skip_fields_regex():
    query = Query(skip_fields=["<regex>header(1|3)"])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2"]
        assert table.header.field_positions == [2]
        assert table.read_rows() == [
            {"header2": "value2"},
        ]


def test_table_skip_fields_position_and_prefix():
    query = Query(skip_fields=[2, "header3"])
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header1"]
        assert table.header.field_positions == [1]
        assert table.read_rows() == [
            {"header1": "value1"},
        ]


def test_table_skip_fields_blank_header():
    query = Query(skip_fields=[""])
    source = "text://header1,,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header1", "header3"]
        assert table.header.field_positions == [1, 3]
        assert table.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_table_skip_fields_blank_header_notation():
    query = Query(skip_fields=["<blank>"])
    source = "text://header1,,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header1", "header3"]
        assert table.header.field_positions == [1, 3]
        assert table.read_rows() == [
            {"header1": "value1", "header3": "value3"},
        ]


def test_table_skip_fields_keyed_source():
    source = [{"id": 1, "name": "london"}, {"id": 2, "name": "paris"}]
    with Table(source, query={"skipFields": ["id"]}) as table:
        assert table.header == ["name"]
        assert table.read_rows() == [{"name": "london"}, {"name": "paris"}]
    with Table(source, query={"skipFields": [1]}) as table:
        assert table.header == ["name"]
        assert table.read_rows() == [{"name": "london"}, {"name": "paris"}]
    with Table(source, query={"skipFields": ["name"]}) as table:
        assert table.header == ["id"]
        assert table.read_rows() == [{"id": 1}, {"id": 2}]
    with Table(source, query={"skipFields": [2]}) as table:
        assert table.header == ["id"]
        assert table.read_rows() == [{"id": 1}, {"id": 2}]


def test_table_limit_fields():
    query = Query(limit_fields=1)
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header1"]
        assert table.header.field_positions == [1]
        assert table.read_rows() == [
            {"header1": "value1"},
        ]


def test_table_offset_fields():
    query = Query(offset_fields=1)
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2", "header3"]
        assert table.header.field_positions == [2, 3]
        assert table.read_rows() == [
            {"header2": "value2", "header3": "value3"},
        ]


def test_table_limit_offset_fields():
    query = Query(limit_fields=1, offset_fields=1)
    source = "text://header1,header2,header3\nvalue1,value2,value3"
    with Table(source, format="csv", query=query) as table:
        assert table.header == ["header2"]
        assert table.header.field_positions == [2]
        assert table.read_rows() == [
            {"header2": "value2"},
        ]


def test_table_pick_rows():
    source = "data/skip-rows.csv"
    query = Query(pick_rows=["1", "2"])
    with Table(source, headers=False, query=query) as table:
        assert table.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
        ]


def test_table_pick_rows_number():
    source = "data/skip-rows.csv"
    query = Query(pick_rows=[3, 5])
    with Table(source, headers=False, query=query) as table:
        assert table.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
        ]


def test_table_pick_rows_regex():
    source = [
        ["# comment"],
        ["name", "order"],
        ["# cat"],
        ["# dog"],
        ["John", 1],
        ["Alex", 2],
    ]
    query = Query(pick_rows=[r"<regex>(name|John|Alex)"])
    with Table(source, query=query) as table:
        assert table.header == ["name", "order"]
        assert table.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_table_skip_rows():
    source = "data/skip-rows.csv"
    query = Query(skip_rows=["#", 5])
    with Table(source, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
        ]


def test_table_skip_rows_excel_empty_column():
    source = "data/skip-rows.xlsx"
    query = Query(skip_rows=[""])
    with Table(source, query=query) as table:
        assert table.read_rows() == [
            {"Table 1": "A", "field2": "B"},
            {"Table 1": 8, "field2": 9},
        ]


def test_table_skip_rows_with_headers():
    source = "data/skip-rows.csv"
    query = Query(skip_rows=["#"])
    with Table(source, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_skip_rows_with_headers_example_from_readme():
    query = Query(skip_rows=["#"])
    source = [["#comment"], ["name", "order"], ["John", 1], ["Alex", 2]]
    with Table(source, query=query) as table:
        assert table.header == ["name", "order"]
        assert table.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_table_skip_rows_regex():
    source = [
        ["# comment"],
        ["name", "order"],
        ["# cat"],
        ["# dog"],
        ["John", 1],
        ["Alex", 2],
    ]
    query = Query(skip_rows=["# comment", r"<regex># (cat|dog)"])
    with Table(source, query=query) as table:
        assert table.header == ["name", "order"]
        assert table.read_rows() == [
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
        ]


def test_table_skip_rows_preset():
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
    query = Query(skip_rows=["<blank>"])
    with Table(source, query=query) as table:
        assert table.header == ["name", "order"]
        assert table.read_rows() == [
            {"name": "Ray", "order": 0},
            {"name": "John", "order": 1},
            {"name": "Alex", "order": 2},
            {"name": None, "order": 3},
            {"name": None, "order": 4},
        ]


def test_table_limit_rows():
    source = "data/long.csv"
    query = Query(limit_rows=1)
    with Table(source, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "a"},
        ]


def test_table_offset_rows():
    source = "data/long.csv"
    query = Query(offset_rows=5)
    with Table(source, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 6, "name": "f"},
        ]


def test_table_limit_offset_rows():
    source = "data/long.csv"
    query = Query(limit_rows=2, offset_rows=2)
    with Table(source, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 3, "name": "c"},
            {"id": 4, "name": "d"},
        ]


def test_table_limit_fields_error_zero_issue_521():
    source = "data/long.csv"
    query = Query(limit_fields=0)
    table = Table(source, query=query)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "query-error"
    assert error.note.count('minimum of 1" at "limitFields')


def test_table_offset_fields_error_zero_issue_521():
    source = "data/long.csv"
    query = Query(offset_fields=0)
    table = Table(source, query=query)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "query-error"
    assert error.note.count('minimum of 1" at "offsetFields')


def test_table_limit_rows_error_zero_issue_521():
    source = "data/long.csv"
    query = Query(limit_rows=0)
    table = Table(source, query=query)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "query-error"
    assert error.note.count('minimum of 1" at "limitRows')


def test_table_offset_rows_error_zero_issue_521():
    source = "data/long.csv"
    query = Query(offset_rows=0)
    table = Table(source, query=query)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "query-error"
    assert error.note.count('minimum of 1" at "offsetRows')


# Header


def test_table_header():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_header_unicode():
    with Table("data/table-unicode-headers.csv") as table:
        assert table.header == ["id", "国人"]
        assert table.read_rows() == [
            {"id": 1, "国人": "english"},
            {"id": 2, "国人": "中国人"},
        ]


def test_table_header_stream_context_manager():
    source = open("data/table.csv", mode="rb")
    with Table(source, format="csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_header_inline():
    source = [[], ["id", "name"], ["1", "english"], ["2", "中国人"]]
    with Table(source, headers=2) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_header_json_keyed():
    source = "text://[" '{"id": 1, "name": "english"},' '{"id": 2, "name": "中国人"}]'
    with Table(source, format="json") as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_header_inline_keyed():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_header_inline_keyed_headers_is_none():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with Table(source, headers=False) as table:
        assert table.header == []
        assert table.read_rows() == [
            {"field1": "id", "field2": "name"},
            {"field1": "1", "field2": "english"},
            {"field1": "2", "field2": "中国人"},
        ]


def test_table_header_xlsx_multiline():
    source = "data/multiline-headers.xlsx"
    dialect = ExcelDialect(fill_merged_cells=True)
    with Table(source, dialect=dialect, headers=[1, 2, 3, 4, 5]) as table:
        header = table.header
        assert header == [
            "Region",
            "Caloric contribution (%)",
            "Cumulative impact of changes on cost of food basket from previous quarter",
            "Cumulative impact of changes on cost of food basket from baseline (%)",
        ]
        assert table.read_rows() == [
            {header[0]: "A", header[1]: "B", header[2]: "C", header[3]: "D"},
        ]


def test_table_header_csv_multiline_headers_join():
    source = "text://k1\nk2\nv1\nv2\nv3"
    with Table(source, format="csv", headers=[[1, 2], ":"]) as table:
        assert table.header == ["k1:k2"]
        assert table.read_rows() == [
            {"k1:k2": "v1"},
            {"k1:k2": "v2"},
            {"k1:k2": "v3"},
        ]


def test_table_header_csv_multiline_headers_duplicates():
    source = "text://k1\nk1\nv1\nv2\nv3"
    with Table(source, format="csv", headers=[1, 2]) as table:
        assert table.header == ["k1"]
        assert table.read_rows() == [
            {"k1": "v1"},
            {"k1": "v2"},
            {"k1": "v3"},
        ]


def test_table_header_strip_and_non_strings():
    source = [[" header ", 2, 3, None], ["value1", "value2", "value3", "value4"]]
    with Table(source, headers=1) as table:
        assert table.header == ["header", "2", "3", ""]
        assert table.read_rows() == [
            {"header": "value1", "2": "value2", "3": "value3", "field4": "value4"},
        ]


# Schema


def test_table_schema():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_schema_provided():
    schema = {
        "fields": [
            {"name": "new1", "type": "string"},
            {"name": "new2", "type": "string"},
        ]
    }
    with Table("data/table.csv", schema=schema) as table:
        assert table.header == ["id", "name"]
        assert table.schema == schema
        assert table.read_rows() == [
            {"new1": "1", "new2": "english"},
            {"new1": "2", "new2": "中国人"},
        ]


def test_table_sync_schema():
    schema = {
        "fields": [{"name": "name", "type": "string"}, {"name": "id", "type": "integer"}]
    }
    with Table("data/sync-schema.csv", schema=schema, sync_schema=True) as table:
        assert table.schema == schema
        assert table.header == ["name", "id"]
        assert table.sample == [["english", "1"], ["中国人", "2"]]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_schema_patch_schema():
    patch_schema = {"fields": {"id": {"name": "new", "type": "string"}}}
    with Table("data/table.csv", patch_schema=patch_schema) as table:
        assert table.header == ["id", "name"]
        assert table.schema == {
            "fields": [
                {"name": "new", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }
        assert table.read_rows() == [
            {"new": "1", "name": "english"},
            {"new": "2", "name": "中国人"},
        ]


def test_table_schema_patch_schema_missing_values():
    patch_schema = {"missingValues": ["1", "2"]}
    with Table("data/table.csv", patch_schema=patch_schema) as table:
        assert table.header == ["id", "name"]
        assert table.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "missingValues": ["1", "2"],
        }
        assert table.read_rows() == [
            {"id": None, "name": "english"},
            {"id": None, "name": "中国人"},
        ]


# Infer


def test_table_infer_type():
    with Table("data/table.csv", infer_type="string") as table:
        assert table.header == ["id", "name"]
        assert table.schema == {
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }
        assert table.read_rows() == [
            {"id": "1", "name": "english"},
            {"id": "2", "name": "中国人"},
        ]


def test_table_infer_names():
    with Table("data/table.csv", infer_names=["new1", "new2"]) as table:
        assert table.header == ["id", "name"]
        assert table.schema == {
            "fields": [
                {"name": "new1", "type": "integer"},
                {"name": "new2", "type": "string"},
            ]
        }
        assert table.read_rows() == [
            {"new1": 1, "new2": "english"},
            {"new1": 2, "new2": "中国人"},
        ]


# Integrity


def test_table_schema_lookup_foreign_keys():
    source = [["name"], [1], [2], [3]]
    lookup = {"other": {("name",): {(1,), (2,), (3,)}}}
    fk = {"fields": ["name"], "reference": {"fields": ["name"], "resource": "other"}}
    with Table(source, lookup=lookup, patch_schema={"foreignKeys": [fk]}) as table:
        for row in table:
            assert row.valid


def test_table_schema_lookup_foreign_keys_error():
    source = [["name"], [1], [2], [4]]
    lookup = {"other": {("name",): {(1,), (2,), (3,)}}}
    fk = {"fields": ["name"], "reference": {"fields": ["name"], "resource": "other"}}
    with Table(source, lookup=lookup, patch_schema={"foreignKeys": [fk]}) as table:
        for row in table:
            if row.row_number == 3:
                assert row.valid is False
                assert row.errors[0].code == "foreign-key-error"
                continue
            assert row.valid


# Stats


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash():
    with Table("data/doublequote.csv") as table:
        table.read_rows()
        assert table.hashing == "md5"
        assert table.stats["hash"] == "d82306001266c4343a2af4830321ead8"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash_md5():
    with Table("data/doublequote.csv", hashing="md5") as table:
        table.read_rows()
        assert table.hashing == "md5"
        assert table.stats["hash"] == "d82306001266c4343a2af4830321ead8"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash_sha1():
    with Table("data/doublequote.csv", hashing="sha1") as table:
        table.read_rows()
        assert table.hashing == "sha1"
        assert table.stats["hash"] == "2842768834a6804d8644dd689da61c7ab71cbb33"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash_sha256():
    with Table("data/doublequote.csv", hashing="sha256") as table:
        table.read_rows()
        assert table.hashing == "sha256"
        assert (
            table.stats["hash"]
            == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
        )


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash_sha512():
    with Table("data/doublequote.csv", hashing="sha512") as table:
        table.read_rows()
        assert table.hashing == "sha512"
        assert (
            table.stats["hash"]
            == "fa555b28a01959c8b03996cd4757542be86293fd49641d61808e4bf9fe4115619754aae9ae6af6a0695585eaade4488ce00dfc40fc4394b6376cd20d6967769c"
        )


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash_compressed():
    with Table("data/doublequote.csv.zip") as table:
        table.read_rows()
        assert table.hashing == "md5"
        assert table.stats["hash"] == "2a72c90bd48c1fa48aec632db23ce8f7"


@pytest.mark.vcr
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_hash_remote():
    with Table(BASE_URL % "data/special/doublequote.csv") as table:
        table.read_rows()
        assert table.hashing == "md5"
        assert table.stats["hash"] == "d82306001266c4343a2af4830321ead8"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_bytes():
    with Table("data/doublequote.csv") as table:
        table.read_rows()
        assert table.stats["bytes"] == 7346


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_bytes_compressed():
    with Table("data/doublequote.csv.zip") as table:
        table.read_rows()
        assert table.stats["bytes"] == 1265


@pytest.mark.vcr
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_stats_bytes_remote():
    with Table(BASE_URL % "data/special/doublequote.csv") as table:
        table.read_rows()
        assert table.stats["bytes"] == 7346


def test_table_stats_fields():
    with Table("data/doublequote.csv") as table:
        table.read_rows()
        assert table.stats["fields"] == 17
        table.open()
        table.read_rows()
        assert table.stats["fields"] == 17


@pytest.mark.vcr
def test_table_stats_fields_remote():
    with Table(BASE_URL % "data/special/doublequote.csv") as table:
        table.read_rows()
        assert table.stats["fields"] == 17


def test_table_stats_rows():
    with Table("data/doublequote.csv") as table:
        table.read_rows()
        assert table.stats["rows"] == 5
        table.open()
        table.read_rows()
        assert table.stats["rows"] == 5


@pytest.mark.vcr
def test_table_stats_rows_remote():
    with Table(BASE_URL % "data/special/doublequote.csv") as table:
        table.read_rows()
        assert table.stats["rows"] == 5


def test_table_stats_rows_significant():
    with Table("data/table1.csv", headers=False) as table:
        table.read_rows()
        assert table.stats["rows"] == 10000


# Open/Close


def test_table_reopen():
    with Table("data/table.csv") as table:

        # Open
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]

        # Re-open
        table.open()
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_reopen_and_infer_volume():
    with Table("data/long.csv", infer_volume=3) as table:
        # Before reset
        assert table.sample == [["1", "a"], ["2", "b"], ["3", "c"]]
        assert table.read_data() == [
            ["id", "name"],
            ["1", "a"],
            ["2", "b"],
            ["3", "c"],
            ["4", "d"],
            ["5", "e"],
            ["6", "f"],
        ]
        assert table.read_rows() == []
        # Reopen table
        table.open()
        # After reopen
        assert table.sample == [["1", "a"], ["2", "b"], ["3", "c"]]
        assert table.read_data() == [
            ["id", "name"],
            ["1", "a"],
            ["2", "b"],
            ["3", "c"],
            ["4", "d"],
            ["5", "e"],
            ["6", "f"],
        ]


def test_table_reopen_generator():
    def generator():
        yield [1]
        yield [2]

    with Table(generator, headers=False) as table:
        # Before reopen
        assert table.read_rows() == [{"field1": 1}, {"field1": 2}]
        # Reset table
        table.open()
        # After reopen
        assert table.read_rows() == [{"field1": 1}, {"field1": 2}]


# Write


def test_table_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.csv"))
    with Table(source) as table:
        table.write(target)
        assert table.stats["rows"] == 2
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_write_format_error_bad_format(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.bad"))
    with Table(source) as table:
        with pytest.raises(FrictionlessException) as excinfo:
            table.write(target)
        error = excinfo.value.error
        assert error.code == "format-error"
        assert (
            error.note == 'cannot create parser "bad". Try installing "frictionless-bad"'
        )


# Integrity


def test_table_integrity_onerror():
    with Table("data/invalid.csv") as table:
        assert table.read_rows()


def test_table_integrity_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    with Table(data, schema=schema, onerror="warn") as table:
        with pytest.warns(UserWarning):
            table.read_rows()


def test_table_integrity_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    with Table(data, schema=schema, onerror="raise") as table:
        with pytest.raises(FrictionlessException):
            table.read_rows()


def test_table_integrity_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    with Table(data, schema=schema, onerror="warn") as table:
        with pytest.warns(UserWarning):
            table.read_rows()


def test_table_integrity_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    with Table(data, schema=schema, onerror="raise") as table:
        with pytest.raises(FrictionlessException):
            table.read_rows()


def test_table_integrity_unique():
    source = [["name"], [1], [2], [3]]
    patch_schema = {"fields": {"name": {"constraints": {"unique": True}}}}
    with Table(source, patch_schema=patch_schema) as table:
        for row in table:
            assert row.valid


def test_table_integrity_unique_error():
    source = [["name"], [1], [2], [2]]
    patch_schema = {"fields": {"name": {"constraints": {"unique": True}}}}
    with Table(source, patch_schema=patch_schema) as table:
        for row in table:
            if row.row_number == 3:
                assert row.valid is False
                assert row.errors[0].code == "unique-error"
                continue
            assert row.valid


def test_table_integrity_primary_key():
    source = [["name"], [1], [2], [3]]
    patch_schema = {"primaryKey": ["name"]}
    with Table(source, patch_schema=patch_schema) as table:
        for row in table:
            assert row.valid


def test_table_integrity_primary_key_error():
    source = [["name"], [1], [2], [2]]
    patch_schema = {"primaryKey": ["name"]}
    with Table(source, patch_schema=patch_schema) as table:
        for row in table:
            if row.row_number == 3:
                assert row.valid is False
                assert row.errors[0].code == "primary-key-error"
                continue
            assert row.valid


def test_table_integrity_foreign_keys():
    source = [["name"], [1], [2], [3]]
    lookup = {"other": {("name",): {(1,), (2,), (3,)}}}
    fk = {"fields": ["name"], "reference": {"fields": ["name"], "resource": "other"}}
    with Table(source, lookup=lookup, patch_schema={"foreignKeys": [fk]}) as table:
        for row in table:
            assert row.valid


def test_table_integrity_foreign_keys_error():
    source = [["name"], [1], [2], [4]]
    lookup = {"other": {("name",): {(1,), (2,), (3,)}}}
    fk = {"fields": ["name"], "reference": {"fields": ["name"], "resource": "other"}}
    with Table(source, lookup=lookup, patch_schema={"foreignKeys": [fk]}) as table:
        for row in table:
            if row.row_number == 3:
                assert row.valid is False
                assert row.errors[0].code == "foreign-key-error"
                continue
            assert row.valid


# Issues


def test_table_reset_on_close_issue_190():
    query = Query(limit_rows=1)
    source = [["1", "english"], ["2", "中国人"]]
    table = Table(source, headers=False, query=query)
    table.open()
    assert table.read_rows() == [{"field1": 1, "field2": "english"}]
    table.open()
    assert table.read_rows() == [{"field1": 1, "field2": "english"}]
    table.close()


def test_table_skip_blank_at_the_end_issue_bco_dmo_33():
    query = Query(skip_rows=["#"])
    source = "data/skip-blank-at-the-end.csv"
    with Table(source, query=query) as table:
        rows = table.read_rows()
        assert table.header == ["test1", "test2"]
        assert rows[0].cells == ["1", "2"]
        assert rows[1].cells == []


def test_table_wrong_encoding_detection_issue_265():
    with Table("data/accent.csv") as table:
        #  Underlaying "chardet" can't detect correct utf-8 here
        assert table.encoding == "iso8859-1"


def test_table_not_existent_local_file_with_no_format_issue_287():
    table = Table("bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad'"


@pytest.mark.vcr
def test_table_not_existent_remote_file_with_no_format_issue_287():
    table = Table("http://example.com/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "404 Client Error: Not Found for url: http://example.com/bad"


@pytest.mark.vcr
def test_table_chardet_raises_remote_issue_305():
    source = "https://gist.githubusercontent.com/roll/56b91d7d998c4df2d4b4aeeefc18cab5/raw/a7a577cd30139b3396151d43ba245ac94d8ddf53/tabulator-issue-305.csv"
    with Table(source) as table:
        assert table.encoding == "utf-8"
        assert len(table.read_rows()) == 343


def test_table_skip_rows_non_string_cell_issue_320():
    source = "data/issue320.xlsx"
    dialect = ExcelDialect(fill_merged_cells=True)
    with pytest.warns(UserWarning):
        with Table(source, dialect=dialect, headers=[10, 11, 12]) as table:
            assert table.header[7] == "Current Population Analysed % of total county Pop"


def test_table_skip_rows_non_string_cell_issue_322():
    query = Query(skip_rows=["1"])
    source = [["id", "name"], [1, "english"], [2, "spanish"]]
    with Table(source, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 2, "name": "spanish"},
        ]
