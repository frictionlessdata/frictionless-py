import pytest
from frictionless import Package, Resource, Schema, system
from frictionless import FrictionlessException


# General


def test_resource_onerror():
    package = Package(resources=[Resource(path="data/invalid.csv")])
    resource = package.resources[0]
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="warn"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.resources[0]
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="raise"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.resources[0]
        with pytest.raises(FrictionlessException):
            resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="warn"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.resources[0]
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="raise"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.resources[0]
        with pytest.raises(FrictionlessException):
            resource.read_rows()
