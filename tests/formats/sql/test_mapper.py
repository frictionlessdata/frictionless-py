import sqlalchemy as sa
from frictionless import Schema, formats


# Read


def test_sql_mapper_read_schema(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    mapper = formats.sql.SqlMapper(engine)
    schema = Schema.describe("data/table.csv")
    table = mapper.write_schema(schema, table_name="table")
    schema = mapper.read_schema(table)
    assert schema.get_field("id").type == "integer"
    assert schema.get_field("name").type == "string"


def test_sql_mapper_read_field(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    mapper = formats.sql.SqlMapper(engine)
    field1 = mapper.read_field(sa.Integer(), name="id")
    field2 = mapper.read_field(sa.Text(), name="name")
    assert field1.type == "integer"
    assert field2.type == "string"


# Write


def test_sql_mapper_write_schema(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    mapper = formats.sql.SqlMapper(engine)
    schema = Schema.describe("data/table.csv")
    table = mapper.write_schema(schema, table_name="table")
    assert table.name == "table"
    assert len(table.columns) == 2
    assert len(table.constraints) == 1


def test_sql_mapper_write_field(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    mapper = formats.sql.SqlMapper(engine)
    schema = Schema.describe("data/table.csv")
    field1, field2 = schema.fields
    sql_type1 = mapper.write_field(field1)
    sql_type2 = mapper.write_field(field2)
    assert sql_type1 is sa.Integer
    assert sql_type2 is sa.Text
