import pytest
from frictionless import Resource, FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


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
    assert error.type == "scheme-error"
    assert error.note.count('scheme "bad" is not supported')


def test_resource_scheme_error_bad_scheme_and_format():
    resource = Resource("bad://bad.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count('scheme "bad" is not supported')


def test_resource_scheme_error_file_not_found():
    resource = Resource("bad.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("bad.csv")


@pytest.mark.vcr
def test_resource_scheme_error_file_not_found_remote():
    resource = Resource("https://example.com/bad.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note[18:] == "Not Found for url: https://example.com/bad.csv"


def test_resource_scheme_error_file_not_found_bad_format():
    resource = Resource("bad.bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("bad.bad")


def test_resource_scheme_error_file_not_found_bad_compression():
    resource = Resource("bad.csv", compression="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("bad.csv")
