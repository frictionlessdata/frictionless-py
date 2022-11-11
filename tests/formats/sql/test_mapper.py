import sqlalchemy as sa
from frictionless import Schema, formats


# Import


def test_sql_mapper_from_schema(sqlite_url):
    mapper = formats.sql.SqlMapper()
    engine = sa.create_engine(sqlite_url)
    schema = Schema.describe("data/table.csv")
    table = mapper.from_schema(schema, engine=engine, table_name="table")
    assert table.name == "table"
    assert len(table.columns) == 2
    assert len(table.constraints) == 1


def test_sql_mapper_from_field(sqlite_url):
    mapper = formats.sql.SqlMapper()
    engine = sa.create_engine(sqlite_url)
    schema = Schema.describe("data/table.csv")
    field1, field2 = schema.fields
    sql_type1 = mapper.from_field(field1, engine=engine)
    sql_type2 = mapper.from_field(field2, engine=engine)
    assert sql_type1 is sa.Integer
    assert sql_type2 is sa.Text


# Export


def test_sql_mapper_to_field():
    mapper = formats.sql.SqlMapper()
    field1 = mapper.to_field(sa.Integer, name="id")
    field2 = mapper.to_field(sa.Text, name="name")
    assert field1.type == "integer"
    assert field2.type == "string"
