import pytest
from frictionless import Resource, Dialect, FrictionlessException, platform


# General


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
    dialect = Dialect(header=False)
    with Resource(source, format="csv", dialect=dialect) as resource:
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
    assert error.type == "encoding-error"
    assert error.note == "unknown encoding: bad"


def test_resource_encoding_error_non_matching_encoding():
    resource = Resource("data/table.csv", encoding="ascii")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "encoding-error"
    if not platform.type == "windows":
        assert error.note[:51] == "'ascii' codec can't decode byte 0xe4 in position 20"
