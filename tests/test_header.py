from frictionless import Header, Field, Schema, Resource


# General


def test_basic():
    header = create_header(["field1", "field2", "field3"])
    assert header.field_positions == [1, 2, 3]
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


# Helpers


def create_header(cells, *, schema=None, field_positions=[]):
    field_positions = field_positions or list(range(1, len(cells) + 1))
    if not schema:
        fields = []
        for field_position in field_positions:
            fields.append(Field({"name": "field%s" % field_position, "type": "any"}))
        schema = Schema({"fields": fields})
    return Header(cells, schema=schema, field_positions=field_positions)
