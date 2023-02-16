import sqlalchemy as sa
from frictionless import Schema, formats


# Read


def test_sql_mapper_read_schema():
    mapper = formats.sql.SqlMapper("sqlite")
    schema = Schema.describe("data/table.csv")
    table = mapper.write_schema(schema, table_name="table")
    schema = mapper.read_schema(table)
    assert schema.get_field("id").type == "integer"
    assert schema.get_field("name").type == "string"


def test_sql_mapper_read_field():
    mapper = formats.sql.SqlMapper("sqlite")
    field1 = mapper.read_field(sa.Column("id", sa.Integer()))
    field2 = mapper.read_field(sa.Column("name", sa.Text()))
    assert field1.type == "integer"
    assert field2.type == "string"


# Write


def test_sql_mapper_write_schema():
    mapper = formats.sql.SqlMapper("sqlite")
    schema = Schema.describe("data/table.csv")
    table = mapper.write_schema(schema, table_name="table")
    assert table.name == "table"
    assert len(table.columns) == 2
    assert len(table.constraints) == 1


def test_sql_mapper_write_field():
    mapper = formats.sql.SqlMapper("sqlite")
    schema = Schema.describe("data/table.csv")
    field1, field2 = schema.fields
    sql_type1 = mapper.write_field(field1)
    sql_type2 = mapper.write_field(field2)
    assert sql_type1 is sa.Integer
    assert sql_type2 is sa.Text
