import os
import sys
import pytest
from frictionless import Package, Resource, Schema, Field, Layout, Detector, helpers
from frictionless import FrictionlessException
from frictionless.plugins.excel import ExcelDialect


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
    assert error.note.count("[Errno 2]") and error.note.count("table.csv")


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


@pytest.mark.skip(reason="Wrong encoding detected")
def test_resource_wrong_encoding_detection_issue_265():
    with Resource("data/accent.csv") as resource:
        assert resource.encoding == "iso8859-1"


def test_resource_not_existent_local_file_with_no_format_issue_287():
    resource = Resource("bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("bad")


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
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.header[7] == "Current Population Analysed % of total county Pop"


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


def test_resource_set_onerror():
    resource = Resource(onerror="raise")
    assert resource.onerror == "raise"
    resource.onerror = "ignore"
    assert resource.onerror == "ignore"


def test_resource_set_trusted():
    resource = Resource(trusted=True)
    assert resource.trusted is True
    resource.trusted = False
    assert resource.trusted is False


def test_resource_set_package():
    test_package_1 = Package()
    resource = Resource(package=test_package_1)
    assert resource.package == test_package_1
    test_package_2 = Package()
    resource.package = test_package_2
    assert resource.package == test_package_2


def test_resource_pprint_1029():
    resource = Resource(
        name="resource",
        title="My Resource",
        description="My Resource for the Guide",
        path="data/table.csv",
    )
    expected = """{'description': 'My Resource for the Guide',
 'name': 'resource',
 'path': 'data/table.csv',
 'title': 'My Resource'}"""
    assert repr(resource) == expected


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
    assert (
        output.count("| id | neighbor_id | name      | population |")
        and output.count("|  1 | 'Ireland'   | 'Britain' | '67'       |")
        and output.count("|  2 | '3'         | 'France'  | 'n/a'      |")
        and output.count("|  3 | '22'        | 'Germany' | '83'       |")
        and output.count("|  4 | None        | 'Italy'   | '60'       |")
        and output.count("|  5 | None        | None      | None       |")
    )
