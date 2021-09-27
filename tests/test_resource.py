import os
import sys
import json
import yaml
import pytest
from frictionless import Resource, Schema, Field, Layout, Detector, helpers
from frictionless import FrictionlessException, describe_resource
from frictionless.plugins.remote import RemoteControl
from frictionless.plugins.excel import ExcelDialect
from frictionless.plugins.json import JsonDialect


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource():
    resource = Resource("data/resource.json")
    assert resource.name == "name"
    assert resource.path == "table.csv"
    assert resource.basepath == "data"
    assert resource.fullpath == "data/table.csv" if IS_UNIX else "data\\table.csv"
    assert resource.profile == "tabular-data-resource"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_dict():
    resource = Resource({"name": "name", "path": "data/table.csv"})
    assert resource == {
        "name": "name",
        "path": "data/table.csv",
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_json():
    resource = Resource("data/resource.json")
    assert resource == {"name": "name", "path": "table.csv"}
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_yaml():
    resource = Resource("data/resource.yaml")
    assert resource == {"name": "name", "path": "table.csv"}
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_yml_issue_644():
    resource = Resource("data/resource.yml")
    assert resource == {"name": "name", "path": "table.csv"}
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource("data/bad.json")
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("bad.json")


@pytest.mark.vcr
def test_resource_from_path_remote():
    resource = Resource(BASEURL % "data/resource.json")
    assert resource.path == "table.csv"
    assert resource.fullpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_from_path_remote_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(BASEURL % "data/bad.json")
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("bad.json")


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_source_non_tabular():
    path = "data/text.txt"
    with Resource(path) as resource:
        assert resource.path == path
        assert resource.data is None
        assert resource.basepath == ""
        assert resource.memory is False
        assert resource.tabular is False
        assert resource.multipart is False
        assert resource.fullpath == path
        if IS_UNIX:
            assert resource.read_bytes() == b"text\n"
            assert resource.stats == {
                "hash": "e1cbb0c3879af8347246f12c559a86b5",
                "bytes": 5,
            }


@pytest.mark.vcr
def test_resource_source_non_tabular_remote():
    path = BASEURL % "data/text.txt"
    with Resource(path) as resource:
        assert resource.path == path
        assert resource.data is None
        assert resource.memory is False
        assert resource.tabular is False
        assert resource.multipart is False
        assert resource.basepath == ""
        assert resource.fullpath == path
        if IS_UNIX:
            assert resource.read_bytes() == b"text\n"
            assert resource.stats == {
                "hash": "e1cbb0c3879af8347246f12c559a86b5",
                "bytes": 5,
            }


def test_resource_source_non_tabular_error_bad_path():
    resource = Resource("data/bad.txt")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_bytes()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note.count("data/bad.txt")


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_source_path():
    path = "data/table.csv"
    resource = Resource({"path": path})
    assert resource.path == path
    assert resource.data is None
    assert resource.memory is False
    assert resource.tabular is True
    assert resource.multipart is False
    assert resource.basepath == ""
    assert resource.fullpath == path
    if IS_UNIX:
        assert (
            resource.read_bytes()
            == b"id,name\n1,english\n2,\xe4\xb8\xad\xe5\x9b\xbd\xe4\xba\xba\n"
        )
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
    assert resource.fragment == [["1", "english"], ["2", "中国人"]]
    assert resource.labels == ["id", "name"]
    assert resource.header == ["id", "name"]
    if IS_UNIX:
        assert resource.stats == {
            "hash": "6c2c61dd9b0e9c6876139a449ed87933",
            "bytes": 30,
            "fields": 2,
            "rows": 2,
        }


def test_resource_source_path_and_basepath():
    resource = Resource(path="table.csv", basepath="data")
    assert resource.path == "table.csv"
    assert resource.basepath == "data"
    assert resource.fullpath == "data/table.csv" if IS_UNIX else "data\\table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_source_path_and_basepath_remote():
    resource = Resource(path="table.csv", basepath=BASEURL % "data")
    assert resource.fullpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_source_path_remote_and_basepath_remote():
    resource = Resource(path=BASEURL % "data/table.csv", basepath=BASEURL % "data")
    assert resource.fullpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_source_path_error_bad_path():
    resource = Resource({"name": "name", "path": "table.csv"})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'table.csv'"


def test_resource_source_path_error_bad_path_not_safe_absolute():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"path": os.path.abspath("data/table.csv")})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("table.csv")


def test_resource_source_path_error_bad_path_not_safe_traversing():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"path": "data/../data/table.csv" if IS_UNIX else "data\\..\\table.csv"})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("table.csv")


def test_resource_source_data():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    resource = Resource({"data": data})
    assert resource.path is None
    assert resource.data == data
    assert resource.memory is True
    assert resource.tabular is True
    assert resource.multipart is False
    assert resource.basepath == ""
    assert resource.fullpath is None
    assert resource.read_bytes() == b""
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    assert resource.sample == data
    assert resource.fragment == data[1:]
    assert resource.labels == ["id", "name"]
    assert resource.header == ["id", "name"]
    assert resource.stats == {
        "hash": "",
        "bytes": 0,
        "fields": 2,
        "rows": 2,
    }


def test_resource_source_path_and_data():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    resource = Resource({"data": data, "path": "path"})
    assert resource.path == "path"
    assert resource.data == data
    assert resource.fullpath is None
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_source_no_path_and_no_data():
    resource = Resource({})
    assert resource.path is None
    assert resource.data == []
    assert resource.fullpath is None
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("is not valid")


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_resource_standard_specs_properties(create_descriptor):
    options = dict(
        path="path",
        name="name",
        profile="profile",
        title="title",
        description="description",
        licenses=[],
        sources=[],
    )
    resource = (
        Resource(**options)
        if not create_descriptor
        else Resource(helpers.create_descriptor(**options))
    )
    assert resource.path == "path"
    assert resource.name == "name"
    assert resource.profile == "profile"
    assert resource.title == "title"
    assert resource.description == "description"
    assert resource.licenses == []
    assert resource.sources == []


def test_resource_official_hash_bytes_rows():
    resource = Resource({"path": "path", "hash": "hash", "bytes": 1, "rows": 1})
    assert resource == {
        "path": "path",
        "stats": {
            "hash": "hash",
            "bytes": 1,
            "rows": 1,
        },
    }


def test_resource_official_hash_bytes_rows_with_hashing_algorithm():
    resource = Resource({"path": "path", "hash": "sha256:hash", "bytes": 1, "rows": 1})
    assert resource == {
        "path": "path",
        "hashing": "sha256",
        "stats": {
            "hash": "hash",
            "bytes": 1,
            "rows": 1,
        },
    }


def test_resource_description_html():
    resource = Resource(description="**test**")
    assert resource.description == "**test**"
    assert resource.description_html == "<p><strong>test</strong></p>"


def test_resource_description_html_multiline():
    resource = Resource(description="**test**\n\nline")
    assert resource.description == "**test**\n\nline"
    assert resource.description_html == "<p><strong>test</strong></p><p>line</p>"


def test_resource_description_html_not_set():
    resource = Resource()
    assert resource.description == ""
    assert resource.description_html == ""


def test_resource_description_text():
    resource = Resource(description="**test**\n\nline")
    assert resource.description == "**test**\n\nline"
    assert resource.description_text == "test line"


def test_resource_description_text_plain():
    resource = Resource(description="It's just a plain text. Another sentence")
    assert resource.description == "It's just a plain text. Another sentence"
    assert resource.description_text == "It's just a plain text. Another sentence"


# Scheme


def test_resource_scheme_file():
    with Resource("data/table.csv") as resource:
        assert resource.scheme == "file"


@pytest.mark.vcr
def test_resource_scheme_https():
    with Resource(BASEURL % "data/table.csv") as resource:
        assert resource.scheme == "https"


def test_resource_scheme_stream():
    with open("data/table.csv", mode="rb") as file:
        with Resource(file, format="csv") as resource:
            assert resource.scheme == "stream"


def test_resource_scheme_buffer():
    with Resource(b"a\nb", format="csv") as resource:
        assert resource.scheme == "buffer"


def test_resource_scheme_error_bad_scheme():
    resource = Resource("bad", scheme="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == 'cannot create loader "bad". Try installing "frictionless-bad"'


def test_resource_scheme_error_bad_scheme_and_format():
    resource = Resource("bad://bad.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == 'cannot create loader "bad". Try installing "frictionless-bad"'


def test_resource_scheme_error_file_not_found():
    resource = Resource("bad.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad.csv'"


@pytest.mark.vcr
def test_resource_scheme_error_file_not_found_remote():
    resource = Resource("https://example.com/bad.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note[18:] == "Not Found for url: https://example.com/bad.csv"


def test_resource_scheme_error_file_not_found_bad_format():
    resource = Resource("bad.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad.bad'"


def test_resource_scheme_error_file_not_found_bad_compression():
    resource = Resource("bad.csv", compression="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad.csv'"


# Format


def test_resource_format_csv():
    with Resource("data/table.csv") as resource:
        assert resource.format == "csv"


def test_resource_format_ndjson():
    with Resource("data/table.ndjson") as resource:
        assert resource.format == "ndjson"


def test_resource_format_tsv():
    with Resource("data/table.tsv") as resource:
        assert resource.format == "tsv"


def test_resource_format_xls():
    with Resource("data/table.xls") as resource:
        assert resource.format == "xls"


def test_resource_format_xlsx():
    with Resource("data/table.xlsx") as resource:
        assert resource.format == "xlsx"


def test_resource_format_error_non_matching_format():
    resource = Resource("data/table.csv", format="xlsx")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'invalid excel file "data/table.csv"'


# Hashing


def test_resource_hashing():
    with Resource("data/table.csv") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "6c2c61dd9b0e9c6876139a449ed87933"


def test_resource_hashing_provided():
    with Resource("data/table.csv", hashing="sha1") as resource:
        resource.read_rows()
        assert resource.hashing == "sha1"
        if IS_UNIX:
            assert resource.stats["hash"] == "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"


def test_resource_hashing_error_bad_hashing():
    resource = Resource("data/table.csv", hashing="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "hashing-error"
    assert error.note == "unsupported hash type bad"


# Encoding


def test_resource_encoding():
    with Resource("data/table.csv") as resource:
        assert resource.encoding == "utf-8"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_encoding_explicit_utf8():
    with Resource("data/table.csv", encoding="utf-8") as resource:
        assert resource.encoding == "utf-8"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_encoding_explicit_latin1():
    with Resource("data/latin1.csv", encoding="latin1") as resource:
        assert resource.encoding == "iso8859-1"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "©"},
        ]


def test_resource_encoding_utf_16():
    # Bytes encoded as UTF-16 with BOM in platform order is detected
    source = "en,English\nja,日本語".encode("utf-16")
    with Resource(source, format="csv", layout={"header": False}) as resource:
        assert resource.encoding == "utf-16"
        assert resource.read_rows() == [
            {"field1": "en", "field2": "English"},
            {"field1": "ja", "field2": "日本語"},
        ]


def test_resource_encoding_error_bad_encoding():
    resource = Resource("data/table.csv", encoding="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "encoding-error"
    assert error.note == "unknown encoding: bad"


def test_resource_encoding_error_non_matching_encoding():
    resource = Resource("data/table.csv", encoding="ascii")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "encoding-error"
    if IS_UNIX:
        assert error.note[:51] == "'ascii' codec can't decode byte 0xe4 in position 20"


# Innerpath


def test_resource_innerpath_local_csv_zip():
    with Resource("data/table.csv.zip") as resource:
        assert resource.innerpath == "table.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_innerpath_local_csv_zip_multiple_files():
    with Resource("data/table-multiple-files.zip", format="csv") as resource:
        assert resource.innerpath == "table-reverse.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "中国人"},
            {"id": 2, "name": "english"},
        ]


def test_resource_innerpath_local_csv_zip_multiple_files_explicit():
    with Resource("data/table-multiple-files.zip", innerpath="table.csv") as resource:
        assert resource.innerpath == "table.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Compression


def test_resource_compression_local_csv_zip():
    with Resource("data/table.csv.zip") as resource:
        assert resource.innerpath == "table.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_compression_local_csv_zip_multiple_files():
    with Resource("data/table-multiple-files.zip", format="csv") as resource:
        assert resource.innerpath == "table-reverse.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "中国人"},
            {"id": 2, "name": "english"},
        ]


def test_resource_compression_local_csv_zip_multiple_open():
    resource = Resource("data/table.csv.zip")

    # Open first time
    resource.open()
    assert resource.header == ["id", "name"]
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    resource.close()

    # Open second time
    resource.open()
    assert resource.header == ["id", "name"]
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    resource.close()


def test_resource_compression_local_csv_gz():
    with Resource("data/table.csv.gz") as resource:
        assert resource.innerpath == ""
        assert resource.compression == "gz"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_compression_stream_csv_zip():
    with open("data/table.csv.zip", "rb") as file:
        with Resource(file, format="csv", compression="zip") as resource:
            assert resource.header == ["id", "name"]
            assert resource.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


def test_resource_compression_stream_csv_gz():
    with open("data/table.csv.gz", "rb") as file:
        with Resource(file, format="csv", compression="gz") as resource:
            assert resource.header == ["id", "name"]
            assert resource.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


@pytest.mark.vcr
def test_resource_compression_remote_csv_zip():
    source = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/data/table.csv.zip"
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_resource_compression_remote_csv_gz():
    source = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/data/table.csv.gz"
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_compression_error_bad():
    resource = Resource("data/table.csv", compression="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "compression-error"
    assert error.note == 'compression "bad" is not supported'


def test_resource_compression_error_invalid_zip():
    source = b"id,filename\n1,archive"
    resource = Resource(source, format="csv", compression="zip")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "compression-error"
    assert error.note == "File is not a zip file"


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python3.8+")
def test_resource_compression_error_invalid_gz():
    source = b"id,filename\n\1,dump"
    resource = Resource(source, format="csv", compression="gz")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "compression-error"
    assert error.note == "Not a gzipped file (b'id')"


def test_resource_compression_legacy_no_value_issue_616():
    with pytest.warns(UserWarning):
        with Resource("data/table.csv", compression="no") as resource:
            assert resource.innerpath == ""
            assert resource.compression == ""
            assert resource.header == ["id", "name"]
            assert resource.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


# Control


def test_resource_control():
    detector = Detector(encoding_function=lambda sample: "utf-8")
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.encoding == "utf-8"
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


@pytest.mark.vcr
def test_resource_control_http_preload():
    control = RemoteControl(http_preload=True)
    with Resource(BASEURL % "data/table.csv", control=control) as resource:
        assert resource.control == {"httpPreload": True}
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


def test_resource_control_bad_property():
    resource = Resource("data/table.csv", control={"bad": True})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "control-error"
    assert error.note.count("bad")


# Dialect


def test_resource_dialect():
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
    assert resource.dialect == dialect
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": " |##"},
    ]


def test_resource_dialect_from_path():
    resource = Resource("data/resource-with-dereferencing.json")
    assert resource == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.dialect == {
        "delimiter": ";",
    }


@pytest.mark.vcr
def test_resource_dialect_from_path_remote():
    resource = Resource(BASEURL % "data/resource-with-dereferencing.json")
    assert resource == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.dialect == {
        "delimiter": ";",
    }


def test_resource_dialect_from_path_error_path_not_safe():
    dialect = os.path.abspath("data/dialect.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "dialect": dialect})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("dialect.json")


def test_resource_dialect_csv_default():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.dialect.delimiter == ","
        assert resource.dialect.line_terminator == "\r\n"
        assert resource.dialect.double_quote is True
        assert resource.dialect.quote_char == '"'
        assert resource.dialect.skip_initial_space is False
        assert resource.layout.header is True
        assert resource.layout.header_rows == [1]
        # All the values are default
        assert resource.dialect == {}
        assert resource.layout == {}
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_csv_delimiter():
    with Resource("data/delimiter.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.dialect == {"delimiter": ";"}
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_dialect_json_property():
    source = b'{"root": [["header1", "header2"], ["value1", "value2"]]}'
    dialect = JsonDialect(property="root")
    with Resource(source, format="json", dialect=dialect) as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
        ]


def test_resource_dialect_bad_property():
    resource = Resource("data/table.csv", dialect={"bad": True})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "dialect-error"
    assert error.note.count("bad")


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


# Schema


DESCRIPTOR_FK = {
    "path": "data/nested.csv",
    "schema": {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "cat", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "foreignKeys": [{"fields": "cat", "reference": {"resource": "", "fields": "id"}}],
    },
}


def test_resource_schema():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "table.csv",
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.schema == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_schema_source_data():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "data": [["id", "name"], ["1", "english"], ["2", "中国人"]],
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.schema == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_schema_source_remote():
    descriptor = {
        "name": "name",
        "profile": "tabular-data-resource",
        "path": "table.csv",
        "schema": "schema.json",
    }
    resource = Resource(descriptor, basepath=BASEURL % "data")
    assert resource.schema == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_schema_from_path():
    resource = Resource("data/resource-with-dereferencing.json")
    assert resource == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.schema == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }


def test_resource_schema_from_path_with_basepath():
    descriptor = {"name": "name", "path": "table.csv", "schema": "schema.json"}
    resource = Resource(descriptor, basepath="data")
    assert resource == descriptor
    assert resource.schema == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }


@pytest.mark.vcr
def test_resource_schema_from_path_remote():
    resource = Resource(BASEURL % "data/resource-with-dereferencing.json")
    assert resource == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.schema == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }


def test_resource_schema_from_path_error_bad_path():
    resource = Resource({"name": "name", "path": "path", "schema": "data/bad.json"})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.code == "schema-error"
    assert error.note.count("bad.json")


def test_resource_schema_from_path_error_path_not_safe():
    schema = os.path.abspath("data/schema.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "schema": schema})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("schema.json")


def test_resource_schema_inferred():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_schema_provided():
    schema = {
        "fields": [
            {"name": "new1", "type": "string"},
            {"name": "new2", "type": "string"},
        ]
    }
    with Resource("data/table.csv", schema=schema) as resource:
        assert resource.schema == schema
        assert resource.labels == ["id", "name"]
        assert resource.header == ["new1", "new2"]
        assert resource.read_rows() == [
            {"new1": "1", "new2": "english"},
            {"new1": "2", "new2": "中国人"},
        ]


def test_resource_schema_unique():
    source = [["name"], [1], [2], [3]]
    detector = Detector(
        schema_patch={"fields": {"name": {"constraints": {"unique": True}}}}
    )
    with Resource(source, detector=detector) as resource:
        for row in resource:
            assert row.valid


def test_resource_schema_unique_error():
    source = [["name"], [1], [2], [2]]
    detector = Detector(
        schema_patch={"fields": {"name": {"constraints": {"unique": True}}}}
    )
    with Resource(source, detector=detector) as resource:
        for row in resource:
            if row.row_number == 3:
                assert row.valid is False
                assert row.errors[0].code == "unique-error"
                continue
            assert row.valid


def test_resource_schema_primary_key():
    source = [["name"], [1], [2], [3]]
    detector = Detector(schema_patch={"primaryKey": ["name"]})
    with Resource(source, detector=detector) as resource:
        for row in resource:
            assert row.valid


def test_resource_schema_primary_key_error():
    source = [["name"], [1], [2], [2]]
    detector = Detector(schema_patch={"primaryKey": ["name"]})
    with Resource(source, detector=detector) as resource:
        for row in resource:
            if row.row_number == 3:
                assert row.valid is False
                assert row.errors[0].code == "primary-key-error"
                continue
            assert row.valid


def test_resource_schema_foreign_keys():
    resource = Resource(DESCRIPTOR_FK)
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid
    assert rows[3].valid
    assert rows[0].to_dict() == {"id": 1, "cat": None, "name": "England"}
    assert rows[1].to_dict() == {"id": 2, "cat": None, "name": "France"}
    assert rows[2].to_dict() == {"id": 3, "cat": 1, "name": "London"}
    assert rows[3].to_dict() == {"id": 4, "cat": 2, "name": "Paris"}


def test_resource_schema_foreign_keys_invalid():
    resource = Resource(DESCRIPTOR_FK, path="data/nested-invalid.csv")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid
    assert rows[3].valid
    assert rows[4].errors[0].code == "foreign-key-error"
    assert rows[0].to_dict() == {"id": 1, "cat": None, "name": "England"}
    assert rows[1].to_dict() == {"id": 2, "cat": None, "name": "France"}
    assert rows[2].to_dict() == {"id": 3, "cat": 1, "name": "London"}
    assert rows[3].to_dict() == {"id": 4, "cat": 2, "name": "Paris"}
    assert rows[4].to_dict() == {"id": 5, "cat": 6, "name": "Rome"}


# Stats


def test_resource_stats_hash():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "d82306001266c4343a2af4830321ead8"


def test_resource_stats_hash_md5():
    with Resource("data/doublequote.csv", hashing="md5") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "d82306001266c4343a2af4830321ead8"


def test_resource_stats_hash_sha1():
    with Resource("data/doublequote.csv", hashing="sha1") as resource:
        resource.read_rows()
        assert resource.hashing == "sha1"
        if IS_UNIX:
            assert resource.stats["hash"] == "2842768834a6804d8644dd689da61c7ab71cbb33"


def test_resource_stats_hash_sha256():
    with Resource("data/doublequote.csv", hashing="sha256") as resource:
        resource.read_rows()
        assert resource.hashing == "sha256"
        if IS_UNIX:
            assert (
                resource.stats["hash"]
                == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
            )


def test_resource_stats_hash_sha512():
    with Resource("data/doublequote.csv", hashing="sha512") as resource:
        resource.read_rows()
        assert resource.hashing == "sha512"
        if IS_UNIX:
            assert (
                resource.stats["hash"]
                == "fa555b28a01959c8b03996cd4757542be86293fd49641d61808e4bf9fe4115619754aae9ae6af6a0695585eaade4488ce00dfc40fc4394b6376cd20d6967769c"
            )


def test_resource_stats_hash_compressed():
    with Resource("data/doublequote.csv.zip") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "2a72c90bd48c1fa48aec632db23ce8f7"


@pytest.mark.vcr
def test_resource_stats_hash_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "d82306001266c4343a2af4830321ead8"


def test_resource_stats_bytes():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        if IS_UNIX:
            assert resource.stats["bytes"] == 7346


def test_resource_stats_bytes_compressed():
    with Resource("data/doublequote.csv.zip") as resource:
        resource.read_rows()
        if IS_UNIX:
            assert resource.stats["bytes"] == 1265


@pytest.mark.vcr
def test_resource_stats_bytes_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        if IS_UNIX:
            assert resource.stats["bytes"] == 7346


def test_resource_stats_fields():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["fields"] == 17
        resource.open()
        resource.read_rows()
        assert resource.stats["fields"] == 17


@pytest.mark.vcr
def test_resource_stats_fields_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["fields"] == 17


def test_resource_stats_rows():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["rows"] == 5
        resource.open()
        resource.read_rows()
        assert resource.stats["rows"] == 5


@pytest.mark.vcr
def test_resource_stats_rows_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["rows"] == 5


def test_resource_stats_rows_significant():
    layout = Layout(header=False)
    with Resource("data/table-1MB.csv", layout=layout) as resource:
        print(resource.read_rows())
        assert resource.stats["rows"] == 10000


# Detector


def test_resource_detector_field_type():
    detector = Detector(field_type="string")
    resource = Resource(path="data/table.csv", detector=detector)
    resource.infer(stats=True)
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.header == ["id", "name"]
    assert resource.read_rows() == [
        {"id": "1", "name": "english"},
        {"id": "2", "name": "中国人"},
    ]


def test_resource_detector_field_names():
    detector = Detector(field_names=["new1", "new2"])
    resource = Resource(path="data/table.csv", detector=detector)
    resource.infer(stats=True)
    assert resource.schema == {
        "fields": [
            {"name": "new1", "type": "integer"},
            {"name": "new2", "type": "string"},
        ]
    }
    assert resource.labels == ["id", "name"]
    assert resource.header == ["new1", "new2"]
    assert resource.read_rows() == [
        {"new1": 1, "new2": "english"},
        {"new1": 2, "new2": "中国人"},
    ]


def test_resource_detector_field_float_numbers():
    data = [["number"], ["1.1"], ["2.2"], ["3.3"]]
    detector = Detector(field_float_numbers=True)
    resource = Resource(data=data, detector=detector)
    resource.infer(stats=True)
    assert resource.schema == {
        "fields": [
            {"name": "number", "type": "number", "floatNumber": True},
        ]
    }
    assert resource.header == ["number"]
    assert resource.read_rows() == [
        {"number": 1.1},
        {"number": 2.2},
        {"number": 3.3},
    ]


def test_resource_detector_field_type_with_open():
    detector = Detector(field_type="string")
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.header == ["id", "name"]
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"id": "1", "name": "english"},
            {"id": "2", "name": "中国人"},
        ]


def test_resource_detector_field_names_with_open():
    detector = Detector(field_names=["new1", "new2"])
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.schema == {
            "fields": [
                {"name": "new1", "type": "integer"},
                {"name": "new2", "type": "string"},
            ]
        }
        assert resource.labels == ["id", "name"]
        assert resource.header == ["new1", "new2"]
        assert resource.read_rows() == [
            {"new1": 1, "new2": "english"},
            {"new1": 2, "new2": "中国人"},
        ]


def test_resource_detector_schema_sync():
    schema = {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "id", "type": "integer"},
        ]
    }
    detector = Detector(schema_sync=True)
    with Resource("data/sync-schema.csv", schema=schema, detector=detector) as resource:
        assert resource.schema == schema
        assert resource.sample == [["name", "id"], ["english", "1"], ["中国人", "2"]]
        assert resource.fragment == [["english", "1"], ["中国人", "2"]]
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_detector_schema_sync_with_infer():
    schema = {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "id", "type": "integer"},
        ]
    }
    detector = Detector(schema_sync=True)
    resource = Resource(path="data/sync-schema.csv", schema=schema, detector=detector)
    resource.infer(stats=True)
    assert resource.schema == schema
    assert resource.sample == [["name", "id"], ["english", "1"], ["中国人", "2"]]
    assert resource.fragment == [["english", "1"], ["中国人", "2"]]
    assert resource.header == ["name", "id"]
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_detector_schema_patch():
    detector = Detector(schema_patch={"fields": {"id": {"name": "ID", "type": "string"}}})
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.schema == {
            "fields": [
                {"name": "ID", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.labels == ["id", "name"]
        assert resource.header == ["ID", "name"]
        assert resource.read_rows() == [
            {"ID": "1", "name": "english"},
            {"ID": "2", "name": "中国人"},
        ]


def test_resource_detector_schema_patch_missing_values():
    detector = Detector(schema_patch={"missingValues": ["1", "2"]})
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.header == ["id", "name"]
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "missingValues": ["1", "2"],
        }
        assert resource.read_rows() == [
            {"id": None, "name": "english"},
            {"id": None, "name": "中国人"},
        ]


def test_resource_detector_schema_patch_with_infer():
    detector = Detector(schema_patch={"fields": {"id": {"name": "ID", "type": "string"}}})
    resource = Resource(path="data/table.csv", detector=detector)
    resource.infer(stats=True)
    assert resource.schema == {
        "fields": [
            {"name": "ID", "type": "string"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.labels == ["id", "name"]
    assert resource.header == ["ID", "name"]
    assert resource.read_rows() == [
        {"ID": "1", "name": "english"},
        {"ID": "2", "name": "中国人"},
    ]


# Onerror


def test_resource_onerror():
    resource = Resource(path="data/invalid.csv")
    assert resource.onerror == "ignore"
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    resource = Resource(data=data, schema=schema, onerror="warn")
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    resource = Resource(data=data, schema=schema, onerror="raise")
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    resource = Resource(data=data, schema=schema, onerror="warn")
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    resource = Resource(data=data, schema=schema, onerror="raise")
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


# Expand


def test_resource_expand():
    resource = Resource({"name": "name", "path": "data/table.csv"})
    resource.expand()
    print(resource)
    assert resource == {
        "name": "name",
        "path": "data/table.csv",
        "profile": "tabular-data-resource",
        "scheme": "file",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "innerpath": "",
        "compression": "",
        "control": {},
        "dialect": {
            "delimiter": ",",
            "lineTerminator": "\r\n",
            "quoteChar": '"',
            "doubleQuote": True,
            "skipInitialSpace": False,
        },
        "layout": {
            "header": True,
            "headerRows": [1],
            "headerJoin": " ",
            "headerCase": True,
        },
        "schema": {"fields": [], "missingValues": [""]},
    }


def test_resource_expand_with_dialect():
    dialect = {"delimiter": "custom"}
    resource = Resource({"name": "name", "path": "data/table.csv", "dialect": dialect})
    resource.expand()
    assert resource == {
        "name": "name",
        "path": "data/table.csv",
        "dialect": {
            "delimiter": "custom",
            "lineTerminator": "\r\n",
            "quoteChar": '"',
            "doubleQuote": True,
            "skipInitialSpace": False,
        },
        "profile": "tabular-data-resource",
        "scheme": "file",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "innerpath": "",
        "compression": "",
        "control": {},
        "layout": {
            "header": True,
            "headerRows": [1],
            "headerJoin": " ",
            "headerCase": True,
        },
        "schema": {"fields": [], "missingValues": [""]},
    }


def test_resource_expand_with_schema():
    schema = {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }
    resource = Resource({"name": "name", "path": "data/table.csv", "schema": schema})
    resource.expand()
    assert resource == {
        "name": "name",
        "path": "data/table.csv",
        "schema": {
            "fields": [
                {
                    "name": "id",
                    "type": "integer",
                    "format": "default",
                    "bareNumber": True,
                },
                {"name": "name", "type": "string", "format": "default"},
            ],
            "missingValues": [""],
        },
        "profile": "tabular-data-resource",
        "scheme": "file",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "innerpath": "",
        "compression": "",
        "control": {},
        "dialect": {
            "delimiter": ",",
            "lineTerminator": "\r\n",
            "quoteChar": '"',
            "doubleQuote": True,
            "skipInitialSpace": False,
        },
        "layout": {
            "header": True,
            "headerRows": [1],
            "headerJoin": " ",
            "headerCase": True,
        },
    }


# Infer


def test_resource_infer():
    resource = Resource(path="data/table.csv")
    resource.infer(stats=True)
    assert resource.metadata_valid
    if IS_UNIX:
        assert resource == {
            "path": "data/table.csv",
            "profile": "tabular-data-resource",
            "name": "table",
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


def test_resource_infer_source_non_tabular():
    resource = Resource(path="data/text.txt")
    resource.infer(stats=True)
    assert resource.metadata_valid
    if IS_UNIX:
        assert resource == {
            "name": "text",
            "path": "data/text.txt",
            "profile": "data-resource",
            "scheme": "file",
            "format": "txt",
            "hashing": "md5",
            "encoding": "utf-8",
            "stats": {
                "hash": "e1cbb0c3879af8347246f12c559a86b5",
                "bytes": 5,
            },
        }


def test_resource_infer_from_path():
    resource = Resource("data/table.csv")
    resource.infer(stats=True)
    assert resource.metadata_valid
    assert resource.path == "data/table.csv"


def test_resource_infer_not_slugified_name_issue_531():
    resource = Resource("data/Table With Data.csv")
    resource.infer(stats=True)
    assert resource.metadata_valid
    assert resource.name == "table-with-data"


# Open/Close


def test_resource_open():
    with Resource("data/table.csv") as resource:
        assert resource.path == "data/table.csv"
        assert resource.scheme == "file"
        assert resource.format == "csv"
        assert resource.encoding == "utf-8"
        assert resource.innerpath == ""
        assert resource.compression == ""
        assert resource.fullpath == "data/table.csv"
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]
        assert resource.header.row_positions == [1]
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_open_read_rows():
    with Resource("data/table.csv") as resource:
        headers = resource.header
        row1, row2 = resource.read_rows()
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


def test_resource_open_row_stream():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert list(resource.row_stream) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
        assert list(resource.row_stream) == []


def test_resource_open_row_stream_iterate():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        for row in resource.row_stream:
            assert len(row) == 2
            assert row.row_number in [1, 2]
            if row.row_number == 1:
                assert row.to_dict() == {"id": 1, "name": "english"}
            if row.row_number == 2:
                assert row.to_dict() == {"id": 2, "name": "中国人"}


def test_resource_open_row_stream_error_cells():
    detector = Detector(field_type="integer")
    with Resource("data/table.csv", detector=detector) as resource:
        row1, row2 = resource.read_rows()
        assert resource.header == ["id", "name"]
        assert row1.errors[0].code == "type-error"
        assert row1.error_cells == {"name": "english"}
        assert row1.to_dict() == {"id": 1, "name": None}
        assert row1.valid is False
        assert row2.errors[0].code == "type-error"
        assert row2.error_cells == {"name": "中国人"}
        assert row2.to_dict() == {"id": 2, "name": None}
        assert row2.valid is False


def test_resource_open_row_stream_blank_cells():
    detector = Detector(schema_patch={"missingValues": ["1", "2"]})
    with Resource("data/table.csv", detector=detector) as resource:
        row1, row2 = resource.read_rows()
        assert resource.header == ["id", "name"]
        assert row1.blank_cells == {"id": "1"}
        assert row1.to_dict() == {"id": None, "name": "english"}
        assert row1.valid is True
        assert row2.blank_cells == {"id": "2"}
        assert row2.to_dict() == {"id": None, "name": "中国人"}
        assert row2.valid is True


def test_resource_open_read_lists():
    with Resource("data/table.csv") as resource:
        assert resource.read_lists() == [
            ["id", "name"],
            ["1", "english"],
            ["2", "中国人"],
        ]


def test_resource_open_list_stream():
    with Resource("data/table.csv") as resource:
        assert list(resource.list_stream) == [
            ["id", "name"],
            ["1", "english"],
            ["2", "中国人"],
        ]
        assert list(resource.list_stream) == []


def test_resource_open_list_stream_iterate():
    with Resource("data/table.csv") as resource:
        for number, cells in enumerate(resource.list_stream):
            assert len(cells) == 2
            if number == 0:
                assert cells == ["id", "name"]
            if number == 1:
                assert cells == ["1", "english"]
            if number == 2:
                assert cells == ["2", "中国人"]


def test_resource_open_empty():
    with Resource("data/empty.csv") as resource:
        assert resource.header.missing
        assert resource.header == []
        assert resource.schema == {}
        assert resource.read_rows() == []


def test_resource_open_without_rows():
    with Resource("data/without-rows.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == []
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "any"},
                {"name": "name", "type": "any"},
            ]
        }


def test_resource_open_without_headers():
    with Resource("data/without-headers.csv") as resource:
        assert resource.labels == []
        assert resource.header.missing
        assert resource.header == ["field1", "field2"]
        assert resource.schema == {
            "fields": [
                {"name": "field1", "type": "integer"},
                {"name": "field2", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
            {"field1": 3, "field2": "german"},
        ]


def test_resource_open_source_error_data():
    resource = Resource(b"[1,2]", format="json")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "source-error"
    assert error.note == "unsupported inline data"


def test_resource_reopen():
    with Resource("data/table.csv") as resource:

        # Open
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]

        # Re-open
        resource.open()
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_reopen_and_detector_sample_size():
    detector = Detector(sample_size=3)
    with Resource("data/long.csv", detector=detector) as resource:
        # Before reset
        assert resource.sample == [["id", "name"], ["1", "a"], ["2", "b"]]
        assert resource.fragment == [["1", "a"], ["2", "b"]]
        assert resource.read_rows() == [
            {"id": 1, "name": "a"},
            {"id": 2, "name": "b"},
            {"id": 3, "name": "c"},
            {"id": 4, "name": "d"},
            {"id": 5, "name": "e"},
            {"id": 6, "name": "f"},
        ]
        # Re-open
        resource.open()
        # After reopen
        assert resource.sample == [["id", "name"], ["1", "a"], ["2", "b"]]
        assert resource.fragment == [["1", "a"], ["2", "b"]]
        assert resource.read_rows() == [
            {"id": 1, "name": "a"},
            {"id": 2, "name": "b"},
            {"id": 3, "name": "c"},
            {"id": 4, "name": "d"},
            {"id": 5, "name": "e"},
            {"id": 6, "name": "f"},
        ]


def test_resource_reopen_generator():
    def generator():
        yield [1]
        yield [2]

    layout = Layout(header=False)
    with Resource(generator, layout=layout) as resource:
        # Before reopen
        assert resource.read_rows() == [{"field1": 1}, {"field1": 2}]
        # Reset resource
        resource.open()
        # After reopen
        assert resource.read_rows() == [{"field1": 1}, {"field1": 2}]


# Read


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_read_bytes():
    resource = Resource(path="data/text.txt")
    bytes = resource.read_bytes()
    if IS_UNIX:
        assert bytes == b"text\n"


def test_resource_read_text():
    resource = Resource(path="data/text.txt")
    text = resource.read_text()
    if IS_UNIX:
        assert text == "text\n"


def test_resource_read_data():
    resource = Resource(path="data/table.json")
    assert resource.read_lists() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_lists():
    resource = Resource(path="data/table.json")
    lists = resource.read_lists()
    assert lists == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_rows():
    resource = Resource(path="data/table.json")
    rows = resource.read_rows()
    assert rows == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


# Write


def test_resource_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.csv")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_write_to_path(tmpdir):
    source = Resource("data/table.csv")
    target = source.write(str(tmpdir.join("table.csv")))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_write_format_error_bad_format(tmpdir):
    source = Resource("data/resource.csv")
    target = Resource(str(tmpdir.join("resource.bad")))
    with pytest.raises(FrictionlessException) as excinfo:
        source.write(target)
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'cannot create parser "bad". Try installing "frictionless-bad"'


# Import/Export


def test_resource_to_copy():
    source = describe_resource("data/table.csv")
    target = source.to_copy()
    assert source == target


def test_resource_to_json(tmpdir):
    target = os.path.join(tmpdir, "resource.json")
    resource = Resource("data/resource.json")
    resource.to_json(target)
    with open(target, encoding="utf-8") as file:
        assert resource == json.load(file)


def test_resource_to_yaml(tmpdir):
    target = os.path.join(tmpdir, "resource.yaml")
    resource = Resource("data/resource.json")
    resource.to_yaml(target)
    with open(target, encoding="utf-8") as file:
        assert resource == yaml.safe_load(file)


def test_to_json_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_json()
    assert text == "{}"


def test_to_yaml_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_yaml()
    assert text == "{}\n"


def test_to_yaml_allow_unicode_issue_844():
    resource = Resource("data/issue-844.csv", encoding="utf-8")
    resource.infer()
    text = resource.to_yaml()
    assert "età" in text


def test_resource_to_view():
    resource = Resource("data/table.csv")
    assert resource.to_view()


# Metadata


def test_resource_metadata_bad_schema_format():
    schema = Schema(
        fields=[
            Field(
                name="name",
                type="boolean",
                format={"trueValues": "Yes", "falseValues": "No"},
            )
        ]
    )
    resource = Resource(name="name", path="data/table.csv", schema=schema)
    assert resource.metadata_valid is False
    assert resource.metadata_errors[0].code == "field-error"


# Issues


def test_resource_reset_on_close_issue_190():
    layout = Layout(header=False, limit_rows=1)
    source = [["1", "english"], ["2", "中国人"]]
    resource = Resource(source, layout=layout)
    resource.open()
    assert resource.read_rows() == [{"field1": 1, "field2": "english"}]
    resource.open()
    assert resource.read_rows() == [{"field1": 1, "field2": "english"}]
    resource.close()


def test_resource_skip_blank_at_the_end_issue_bco_dmo_33():
    layout = Layout(skip_rows=["#"])
    source = "data/skip-blank-at-the-end.csv"
    with Resource(source, layout=layout) as resource:
        rows = resource.read_rows()
        assert resource.header == ["test1", "test2"]
        assert rows[0].cells == ["1", "2"]
        assert rows[1].cells == []


def test_resource_wrong_encoding_detection_issue_265():
    with Resource("data/accent.csv") as resource:
        assert resource.encoding == "iso8859-1"


def test_resource_not_existent_local_file_with_no_format_issue_287():
    resource = Resource("bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'bad'"


@pytest.mark.vcr
def test_resource_not_existent_remote_file_with_no_format_issue_287():
    resource = Resource("http://example.com/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "404 Client Error: Not Found for url: http://example.com/bad"


@pytest.mark.vcr
def test_resource_chardet_raises_remote_issue_305():
    source = "https://gist.githubusercontent.com/roll/56b91d7d998c4df2d4b4aeeefc18cab5/raw/a7a577cd30139b3396151d43ba245ac94d8ddf53/tabulator-issue-305.csv"
    with Resource(source) as resource:
        assert resource.encoding == "utf-8"
        assert len(resource.read_rows()) == 343


def test_resource_skip_rows_non_string_cell_issue_320():
    source = "data/issue-320.xlsx"
    dialect = ExcelDialect(fill_merged_cells=True)
    layout = Layout(header_rows=[10, 11, 12])
    with pytest.warns(UserWarning):
        with Resource(source, dialect=dialect, layout=layout) as resource:
            assert (
                resource.header[7] == "Current Population Analysed % of total county Pop"
            )


def test_resource_skip_rows_non_string_cell_issue_322():
    layout = Layout(skip_rows=["1"])
    source = [["id", "name"], [1, "english"], [2, "spanish"]]
    with Resource(source, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "spanish"},
        ]


def test_resource_relative_parent_path_with_trusted_option_issue_171():
    path = "data/../data/table.csv" if IS_UNIX else "data\\..\\data\\table.csv"
    # trusted=false (default)
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"path": path})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("table.csv")
    # trusted=true
    resource = Resource({"path": path}, trusted=True)
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_preserve_format_from_descriptor_on_infer_issue_188():
    resource = Resource({"path": "data/table.csvformat", "format": "csv"})
    resource.infer(stats=True)
    if IS_UNIX:
        assert resource == {
            "path": "data/table.csvformat",
            "format": "csv",
            "profile": "tabular-data-resource",
            "name": "table",
            "scheme": "file",
            "hashing": "md5",
            "encoding": "utf-8",
            "schema": {
                "fields": [
                    {"name": "city", "type": "string"},
                    {"name": "population", "type": "integer"},
                ]
            },
            "stats": {
                "hash": "f71969080b27963b937ca28cdd5f63b9",
                "bytes": 58,
                "fields": 2,
                "rows": 3,
            },
        }
