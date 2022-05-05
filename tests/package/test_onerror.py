import pytest
from frictionless import Package, Resource, helpers
from frictionless import FrictionlessException


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Onerror


def test_resource_onerror():
    package = Package(resources=[Resource(path="data/invalid.csv")])
    resource = package.resources[0]
    assert package.onerror == "ignore"
    assert resource.onerror == "ignore"
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="warn")
    resource = package.resources[0]
    assert package.onerror == "warn"
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    package = Package({"resources": [{"data": data, "schema": schema}]}, onerror="raise")
    resource = package.resources[0]
    assert package.onerror == "raise"
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="warn")
    resource = package.resources[0]
    assert package.onerror == "warn"
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    package = Package({"resources": [{"data": data, "schema": schema}]}, onerror="raise")
    resource = package.resources[0]
    assert package.onerror == "raise"
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()
