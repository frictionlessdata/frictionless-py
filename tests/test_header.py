from frictionless import Field, Schema, Resource


# General


def test_basic():
    resource = Resource(data=[["field1", "field2", "field3"], [1, 2, 3]])
    header = resource.read_header()
    assert header.field_positions == [1, 2, 3]
    assert header.row_positions == [1]
    assert header.errors == []
    assert header == ["field1", "field2", "field3"]


def test_extra_header():
    schema = Schema(fields=[Field(name="id")])
    resource = Resource(path="data/table.csv", schema=schema)
    header = resource.read_header()
    assert header == ["id", "name"]
    assert header.valid is False


def test_missing_header():
    schema = Schema(fields=[Field(name="id"), Field(name="name"), Field(name="extra")])
    resource = Resource(path="data/table.csv", schema=schema)
    header = resource.read_header()
    assert header == ["id", "name"]
    assert header.valid is False
