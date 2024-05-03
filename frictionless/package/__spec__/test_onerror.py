import pytest

from frictionless import FrictionlessException, Package, Resource, Schema, system

# General


def test_resource_onerror():
    package = Package(resources=[Resource(path="data/invalid.csv")])
    resource = package.get_table_resource("invalid")
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="warn"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.get_table_resource("memory")
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="raise"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.get_table_resource("memory")
        with pytest.raises(FrictionlessException):
            resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="warn"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.get_table_resource("memory")
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="raise"):
        package = Package(resources=[Resource(data=data, schema=schema)])
        resource = package.get_table_resource("memory")
        with pytest.raises(FrictionlessException):
            resource.read_rows()
