import sys
import pytest
import textwrap
from importlib import import_module
from frictionless import Package, Resource, Control, Detector, platform
from frictionless import Dialect, FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource():
    resource = Resource("data/resource.json")
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
    resource = Resource({"name": "name", "path": "data/table.csv"})
    assert resource.to_descriptor() == {"name": "name", "path": "data/table.csv"}
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_json():
    resource = Resource("data/resource.json")
    assert resource.to_descriptor() == {"name": "name", "path": "table.csv"}
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_yaml():
    resource = Resource("data/resource.yaml")
    assert resource.to_descriptor() == {"name": "name", "path": "table.csv"}
    assert resource.basepath == "data"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_from_path_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource("data/bad.resource.json")
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("bad.resource.json")


@pytest.mark.vcr
def test_resource_from_path_remote():
    resource = Resource(BASEURL % "data/resource.json")
    assert resource.path == "table.csv"
    assert resource.basepath == BASEURL % "data"
    assert resource.normpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_from_url_standards_v0():
    resource = Resource.from_descriptor({"url": BASEURL % "data/table.csv"})
    assert resource.path == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_from_path_remote_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(BASEURL % "data/bad.resource.json")
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("bad.resource.json")


def test_resource_source_non_tabular():
    path = "data/text.txt"
    with Resource(path) as resource:
        assert resource.path == path
        assert resource.data is None
        assert resource.type == "file"
        assert resource.basepath is None
        assert resource.memory is False
        assert resource.multipart is False
        assert resource.normpath == path
        if not platform.type == "windows":
            assert resource.read_bytes() == b"text\n"
            assert resource.stats.to_descriptor() == {
                "md5": "e1cbb0c3879af8347246f12c559a86b5",
                "sha256": "b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733",
                "bytes": 5,
            }


@pytest.mark.vcr
def test_resource_source_non_tabular_remote():
    path = BASEURL % "data/text.txt"
    with Resource(path) as resource:
        assert resource.path == path
        assert resource.data is None
        assert resource.type == "file"
        assert resource.memory is False
        assert resource.multipart is False
        assert resource.basepath is None
        assert resource.normpath == path
        if not platform.type == "windows":
            assert resource.read_bytes() == b"text\n"
            assert resource.stats.to_descriptor() == {
                "md5": "e1cbb0c3879af8347246f12c559a86b5",
                "sha256": "b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733",
                "bytes": 5,
            }


def test_resource_source_non_tabular_error_bad_path():
    resource = Resource("data/bad.txt")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_bytes()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("data/bad.txt")


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_source_path():
    path = "data/table.csv"
    resource = Resource({"path": path})
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
        assert resource.stats.to_descriptor() == {
            "md5": "6c2c61dd9b0e9c6876139a449ed87933",
            "sha256": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
            "bytes": 30,
            "fields": 2,
            "rows": 2,
        }


def test_resource_source_path_and_basepath():
    resource = Resource(path="table.csv", basepath="data")
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
    resource = Resource(path="table.csv", basepath=BASEURL % "data")
    assert resource.normpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_resource_source_path_remote_and_basepath_remote():
    resource = Resource(path=BASEURL % "data/table.csv", basepath=BASEURL % "data")
    assert resource.normpath == BASEURL % "data/table.csv"
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_source_path_error_bad_path():
    resource = Resource({"name": "name", "path": "table.csv"})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("table.csv")


def test_resource_source_data():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with Resource({"data": data}) as resource:
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
        assert resource.stats.to_descriptor() == {
            "fields": 2,
            "rows": 2,
        }


def test_resource_source_no_path_and_no_data():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource.from_descriptor({})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == 'one of the properties "path" or "data" is required'


def test_resource_source_both_path_and_data():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"data": data, "path": "path"})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == 'properties "path" and "data" is mutually exclusive'


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_resource_standard_specs_properties(create_descriptor):
    helpers = import_module("frictionless.helpers")
    options = dict(
        path="path",
        name="name",
        title="title",
        description="description",
        profiles=[],
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
    assert resource.title == "title"
    assert resource.description == "description"
    assert resource.profiles == []
    assert resource.licenses == []
    assert resource.sources == []


def test_resource_official_hash_bytes_rows():
    resource = Resource({"path": "path", "hash": "hash", "bytes": 1})
    assert resource.to_descriptor() == {
        "path": "path",
        "stats": {
            "md5": "hash",
            "bytes": 1,
        },
    }


def test_resource_official_hash_bytes_rows_with_hashing_algorithm():
    resource = Resource({"path": "path", "hash": "sha256:hash", "bytes": 1})
    assert resource.to_descriptor() == {
        "path": "path",
        "stats": {
            "sha256": "hash",
            "bytes": 1,
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
    assert resource.description is None
    assert resource.description_html == ""


def test_resource_description_text():
    resource = Resource(description="**test**\n\nline")
    assert resource.description == "**test**\n\nline"
    assert resource.description_text == "test line"


def test_resource_description_text_plain():
    resource = Resource(description="It's just a plain text. Another sentence")
    assert resource.description == "It's just a plain text. Another sentence"
    assert resource.description_text == "It's just a plain text. Another sentence"


def test_resource_set_base_path():
    resource = Resource(basepath="/data")
    assert resource.basepath == "/data"
    resource.basepath = "/data/csv"
    assert resource.basepath == "/data/csv"


def test_resource_set_detector():
    detector_set_init = Detector(field_missing_values=["na"])
    resource = Resource("data/table.csv", detector=detector_set_init)
    assert resource.detector == detector_set_init
    detector_set = Detector(sample_size=3)
    resource.detector = detector_set
    assert resource.detector == detector_set


def test_resource_set_package():
    test_package_1 = Package()
    resource = Resource(package=test_package_1)
    assert resource.package == test_package_1
    test_package_2 = Package()
    resource.package = test_package_2
    assert resource.package == test_package_2


def test_resource_pprint():
    resource = Resource(
        name="resource",
        title="My Resource",
        description="My Resource for the Guide",
        path="data/table.csv",
    )
    expected = """
    {'name': 'resource',
     'title': 'My Resource',
     'description': 'My Resource for the Guide',
     'path': 'data/table.csv'}
    """
    assert repr(resource) == textwrap.dedent(expected).strip()


def test_resource_summary_valid_resource():
    resource = Resource("data/capital-valid.csv")
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
    resource = Resource("data/countries.csv")
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
    resource = Resource(source, dialect=dialect)
    resource.open()
    assert resource.read_rows(size=1) == [{"field1": 1, "field2": "english"}]
    resource.open()
    assert resource.read_rows(size=1) == [{"field1": 1, "field2": "english"}]
    resource.close()


def test_resource_skip_blank_at_the_end_issue_bco_dmo_33():
    dialect = Dialect(comment_char="#")
    source = "data/skip-blank-at-the-end.csv"
    with Resource(source, dialect=dialect) as resource:
        rows = resource.read_rows()
        assert resource.header == ["test1", "test2"]
        assert rows[0].cells == ["1", "2"]
        assert rows[1].cells == []


@pytest.mark.skip
def test_resource_wrong_encoding_detection_issue_265():
    with Resource("data/accent.csv") as resource:
        assert resource.encoding == "iso8859-1"


def test_resource_not_existent_local_file_with_no_format_issue_287():
    resource = Resource("bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("bad")


@pytest.mark.vcr
def test_resource_not_existent_remote_file_with_no_format_issue_287():
    resource = Resource("http://example.com/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note == "404 Client Error: Not Found for url: http://example.com/bad"


@pytest.mark.vcr
def test_resource_chardet_raises_remote_issue_305():
    source = "https://gist.githubusercontent.com/roll/56b91d7d998c4df2d4b4aeeefc18cab5/raw/a7a577cd30139b3396151d43ba245ac94d8ddf53/tabulator-issue-305.csv"
    with Resource(source) as resource:
        assert resource.encoding == "utf-8"
        assert len(resource.read_rows()) == 343


def test_resource_skip_rows_non_string_cell_issue_320():
    source = "data/issue-320.xlsx"
    dialect = Dialect(
        header_rows=[10, 11, 12],
        controls=[Control.from_descriptor({"type": "excel", "fillMergedCells": True})],
    )
    with Resource(source, dialect=dialect) as resource:
        assert resource.header[7] == "Current Population Analysed % of total county Pop"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_preserve_format_from_descriptor_on_infer_issue_188():
    resource = Resource({"path": "data/table.csvformat", "format": "csv"})
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csvformat",
        "type": "table",
        "format": "csv",
        "scheme": "file",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "schema": {
            "fields": [
                {"name": "city", "type": "string"},
                {"name": "population", "type": "integer"},
            ]
        },
        "stats": {
            "md5": "f71969080b27963b937ca28cdd5f63b9",
            "sha256": "350e813ea15d84c697a7b03446a8fa9d7fca9883167ad70986a173c29f8253fd",
            "bytes": 58,
            "fields": 2,
            "rows": 3,
        },
    }


def test_resource_path_with_brackets_issue_1206():
    resource = Resource.from_descriptor({"path": "data/[table].csv"})
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
