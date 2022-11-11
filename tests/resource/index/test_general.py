import sqlalchemy as sa
from frictionless import Resource


# General


def test_resource_index(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    resource = Resource("data/table.csv")
    resource.index(engine=engine)
    result = engine.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
    )
    print(list(result))
    assert False
