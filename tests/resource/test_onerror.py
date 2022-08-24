import pytest
from frictionless import Resource, Schema, FrictionlessException, system


# General


def test_resource_onerror():
    resource = Resource(path="data/invalid.csv")
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="warn"):
        resource = Resource(data=data, schema=schema)
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="raise"):
        resource = Resource(data=data, schema=schema)
        with pytest.raises(FrictionlessException):
            resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="warn"):
        resource = Resource(data=data, schema=schema)
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="raise"):
        resource = Resource(data=data, schema=schema)
        with pytest.raises(FrictionlessException):
            resource.read_rows()
