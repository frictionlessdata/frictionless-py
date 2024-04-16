import textwrap
from importlib import import_module

import pytest

from frictionless import Detector, FrictionlessException, Package, Resource, platform

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource_from_path_error_bad_path():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource("data/bad.resource.json")
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("bad.resource.json")


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
        assert resource.type == "text"
        assert resource.basepath is None
        assert resource.memory is False
        assert resource.multipart is False
        assert resource.normpath == path
        if not platform.type == "windows":
            assert resource.read_bytes() == b"text\n"
            assert resource.stats.md5 == "e1cbb0c3879af8347246f12c559a86b5"
            assert (
                resource.stats.sha256
                == "b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733"
            )
            assert resource.stats.bytes == 5


@pytest.mark.vcr
def test_resource_source_non_tabular_remote():
    path = BASEURL % "data/text.txt"
    with Resource(path) as resource:
        assert resource.path == path
        assert resource.data is None
        assert resource.type == "text"
        assert resource.memory is False
        assert resource.multipart is False
        assert resource.basepath is None
        assert resource.normpath == path
        if not platform.type == "windows":
            assert resource.read_bytes() == b"text\n"
            assert resource.stats.md5 == "e1cbb0c3879af8347246f12c559a86b5"
            assert (
                resource.stats.sha256
                == "b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733"
            )
            assert resource.stats.bytes == 5


def test_resource_source_non_tabular_error_bad_path():
    resource = Resource("data/bad.txt")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_bytes()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("data/bad.txt")


def test_resource_source_no_path_and_no_data():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource.from_descriptor({"name": "name"})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == 'one of the properties "path" or "data" is required'


def test_resource_source_both_path_and_data():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "data": data, "path": "path"})
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
        Resource(**options)  # type: ignore
        if not create_descriptor
        else Resource(helpers.create_descriptor(**options))
    )
    assert resource.path == "path"
    assert resource.name == "name"
    assert resource.title == "title"
    assert resource.description == "description"
    assert resource.profile is None
    assert resource.licenses == []
    assert resource.sources == []


def test_resource_official_hash_bytes_rows():
    resource = Resource({"name": "name", "path": "path", "hash": "hash", "bytes": 1})
    descriptor = resource.to_descriptor()
    assert descriptor["hash"] == "hash"
    assert descriptor["bytes"] == 1


def test_resource_official_hash_bytes_rows_with_hashing_algorithm():
    resource = Resource(
        {"name": "name", "path": "path", "hash": "sha256:hash", "bytes": 1}
    )
    descriptor = resource.to_descriptor()
    assert descriptor["hash"] == "sha256:hash"
    assert descriptor["bytes"] == 1


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


@pytest.mark.skip
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


# Bugs


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


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_preserve_format_from_descriptor_on_infer_issue_188():
    resource = Resource({"name": "name", "path": "data/table.csvformat", "format": "csv"})
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
