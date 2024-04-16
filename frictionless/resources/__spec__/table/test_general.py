import sys

import pytest

from frictionless import Control, Dialect, platform
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource():
    resource = TableResource.from_descriptor("data/resource.json")
    assert resource.name == "name"
    assert resource.path == "table.csv"
    assert resource.basepath == "data"
    assert (
        resource.normpath == "data/table.csv"
        if not platform.type == "windows"
        else "data\\table.csv"
    )
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_dict():
    resource = TableResource.from_descriptor({"name": "name", "path": "data/table.csv"})
    assert resource.to_descriptor() == {
        "name": "name",
        "type": "table",
        "path": "data/table.csv",
        "scheme": "file",
        "format": "csv",
        "mediatype": "text/csv",
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_json():
    resource = TableResource.from_descriptor("data/resource.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "type": "table",
        "path": "table.csv",
        "scheme": "file",
        "format": "csv",
        "mediatype": "text/csv",
    }
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_yaml():
    resource = TableResource.from_descriptor("data/resource.yaml")
    assert resource.to_descriptor() == {
        "name": "name",
        "type": "table",
        "path": "table.csv",
        "scheme": "file",
        "format": "csv",
        "mediatype": "text/csv",
    }
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_from_path_remote():
    resource = TableResource.from_descriptor(BASEURL % "data/resource.json")
    assert resource.path == "table.csv"
    assert resource.basepath == BASEURL % "data"
    assert resource.normpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_from_url_standards_v0():
    resource = TableResource.from_descriptor(
        {"name": "name", "url": BASEURL % "data/table.csv"}
    )
    assert resource.path == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_source_path():
    path = "data/table.csv"
    resource = TableResource.from_descriptor({"name": "name", "path": path})
    resource.infer()
    assert resource.path == path
    assert resource.data is None
    assert resource.type == "table"
    assert resource.memory is False
    assert resource.multipart is False
    assert resource.basepath is None
    assert resource.normpath == path
    if not platform.type == "windows":
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
    if not platform.type == "windows":
        assert resource.stats.md5 == "6c2c61dd9b0e9c6876139a449ed87933"
        assert (
            resource.stats.sha256
            == "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
        )
        assert resource.stats.bytes == 30
        assert resource.stats.fields == 2
        assert resource.stats.rows == 2


def test_resource_source_path_and_basepath():
    resource = TableResource(path="table.csv", basepath="data")
    assert resource.path == "table.csv"
    assert resource.basepath == "data"
    assert (
        resource.normpath == "data/table.csv"
        if not platform.type == "windows"
        else "data\\table.csv"
    )
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_source_path_and_basepath_remote():
    resource = TableResource(path="table.csv", basepath=BASEURL % "data")
    assert resource.normpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_source_path_remote_and_basepath_remote():
    resource = TableResource(path=BASEURL % "data/table.csv", basepath=BASEURL % "data")
    assert resource.normpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_source_data():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with TableResource.from_descriptor({"name": "name", "data": data}) as resource:
        assert resource.path is None
        assert resource.data == data
        assert resource.memory is True
        assert resource.tabular is True
        assert resource.multipart is False
        assert resource.basepath is None
        assert resource.read_bytes() == b""
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
        assert resource.sample == data
        assert resource.fragment == data[1:]
        assert resource.labels == ["id", "name"]
        assert resource.header == ["id", "name"]
        assert resource.stats.fields == 2
        assert resource.stats.rows == 2


def test_resource_summary_valid_resource():
    resource = TableResource(path="data/capital-valid.csv")
    output = resource.to_view()
    assert (
        output.count("| id | name     |")
        and output.count("|  1 | 'London' |")
        and output.count("|  2 | 'Berlin' |")
        and output.count("|  3 | 'Paris'  |")
        and output.count("|  4 | 'Madrid' |")
        and output.count("|  5 | 'Rome'   |")
    )


def test_resource_summary_invalid_resource():
    resource = TableResource(path="data/countries.csv")
    output = resource.to_view()
    assert output.count("| id | neighbor_id | name      | population |")
    assert output.count("|  1 | 'Ireland'   | 'Britain' | '67'       |")
    assert output.count("|  2 | '3'         | 'France'  | 'n/a'      |")
    assert output.count("|  3 | '22'        | 'Germany' | '83'       |")
    assert output.count("|  4 | None        | 'Italy'   | '60'       |")
    assert output.count("|  5 | None        | None      | None       |")


# Bugs


def test_resource_reset_on_close_issue_190():
    dialect = Dialect(header=False)
    source = [["1", "english"], ["2", "中国人"]]
    resource = TableResource(data=source, dialect=dialect)
    resource.open()
    assert resource.read_rows(size=1) == [{"field1": 1, "field2": "english"}]
    resource.open()
    assert resource.read_rows(size=1) == [{"field1": 1, "field2": "english"}]
    resource.close()


def test_resource_skip_blank_at_the_end_issue_bco_dmo_33():
    dialect = Dialect(comment_char="#")
    source = "data/skip-blank-at-the-end.csv"
    with TableResource(path=source, dialect=dialect) as resource:
        rows = resource.read_rows()
        assert resource.header == ["test1", "test2"]
        assert rows[0].cells == ["1", "2"]
        assert rows[1].cells == []


# The encoding is now detected as "mac-roman"
# We consider it's valid behaviour as data can be sucesefully read
# https://github.com/frictionlessdata/framework/issues/1347
def test_resource_wrong_encoding_detection_issue_265():
    with TableResource(path="data/accent.csv") as resource:
        #  assert resource.encoding == "iso8859-1"
        assert resource.encoding == "mac-roman"
        assert len(resource.read_rows()) == 2


@pytest.mark.vcr
def test_resource_chardet_raises_remote_issue_305():
    source = "https://gist.githubusercontent.com/roll/56b91d7d998c4df2d4b4aeeefc18cab5/raw/a7a577cd30139b3396151d43ba245ac94d8ddf53/tabulator-issue-305.csv"
    with TableResource(path=source) as resource:
        assert resource.encoding == "utf-8"
        assert len(resource.read_rows()) == 343


def test_resource_skip_rows_non_string_cell_issue_320():
    source = "data/issue-320.xlsx"
    dialect = Dialect(
        header_rows=[10, 11, 12],
        controls=[Control.from_descriptor({"type": "excel", "fillMergedCells": True})],
    )
    with TableResource(path=source, dialect=dialect) as resource:
        assert resource.header[7] == "Current Population Analysed % of total county Pop"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_preserve_format_from_descriptor_on_infer_issue_188():
    resource = TableResource.from_descriptor(
        {"name": "name", "path": "data/table.csvformat", "format": "csv"}
    )
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "name",
        "path": "data/table.csvformat",
        "type": "table",
        "format": "csv",
        "scheme": "file",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "hash": "sha256:350e813ea15d84c697a7b03446a8fa9d7fca9883167ad70986a173c29f8253fd",
        "bytes": 58,
        "fields": 2,
        "rows": 3,
        "schema": {
            "fields": [
                {"name": "city", "type": "string"},
                {"name": "population", "type": "integer"},
            ]
        },
    }


def test_resource_path_with_brackets_issue_1206():
    resource = TableResource.from_descriptor({"name": "name", "path": "data/[table].csv"})
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
