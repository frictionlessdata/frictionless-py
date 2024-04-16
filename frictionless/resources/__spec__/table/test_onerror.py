import pytest

from frictionless import FrictionlessException, Schema, system
from frictionless.resources import TableResource

# General


def test_resource_onerror():
    resource = TableResource(path="data/invalid.csv")
    assert resource.read_rows()


def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="warn"):
        resource = TableResource(data=data, schema=schema)
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "bad", "type": "integer"}]})
    with system.use_context(onerror="raise"):
        resource = TableResource(data=data, schema=schema)
        with pytest.raises(FrictionlessException):
            resource.read_rows()


def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="warn"):
        resource = TableResource(data=data, schema=schema)
        with pytest.warns(UserWarning):
            resource.read_rows()


def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    with system.use_context(onerror="raise"):
        resource = TableResource(data=data, schema=schema)
        with pytest.raises(FrictionlessException):
            resource.read_rows()
