import pytest
from frictionless import Resource, Detector, helpers, FrictionlessException
from frictionless.plugins.remote import RemoteControl


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


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
