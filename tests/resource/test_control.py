import pytest
from frictionless import Resource, Dialect, Detector, FrictionlessException
from frictionless.plugins.remote import RemoteControl


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource_control():
    detector = Detector(encoding_function=lambda buffer: "utf-8")
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.encoding == "utf-8"
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


@pytest.mark.vcr
def test_resource_control_http_preload():
    dialect = Dialect(controls=[RemoteControl(http_preload=True)])
    with Resource(BASEURL % "data/table.csv", dialect=dialect) as resource:
        assert resource.dialect.get_control("remote").http_preload is True
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


@pytest.mark.skip
def test_resource_control_bad_property():
    dialect = Dialect.from_descriptor({"bad": True})
    resource = Resource("data/table.csv", dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "control-error"
    assert error.note.count("bad")
