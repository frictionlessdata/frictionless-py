import sqlalchemy as sa
from frictionless import Resource


# General


def test_resource_index(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    resource = Resource("data/table.csv", name="index")
    resource.index(postgresql_url)
    result = engine.execute("SELECT * FROM index")
    assert list(result) == [
        (1, "english"),
        (2, "中国人"),
    ]
