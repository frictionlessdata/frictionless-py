import pytest
from frictionless import Resource, FrictionlessException, platform


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
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


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
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
    assert error.type == "format-error"
    assert error.note.count('format "bad" is not supported')
