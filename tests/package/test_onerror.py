import pytest
from frictionless import Package, Resource, Schema
from frictionless import FrictionlessException


# General


def test_resource_onerror():
    package = Package(resources=[Resource(path="data/invalid.csv")])
    resource = package.resources[0]
    assert package.onerror == "ignore"
    assert resource.onerror == "ignore"
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="warn")
    resource = package.resources[0]
    assert package.onerror == "warn"
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="raise")
    resource = package.resources[0]
    assert package.onerror == "raise"
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="warn")
    resource = package.resources[0]
    assert package.onerror == "warn"
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    package = Package(resources=[Resource(data=data, schema=schema)], onerror="raise")
    resource = package.resources[0]
    assert package.onerror == "raise"
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()
