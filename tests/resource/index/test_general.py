import pytest
import sqlalchemy as sa
from frictionless import Resource, platform


# General


@pytest.mark.skipif(platform.type == "darwin", reason="Skip SQL test in MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    resource = Resource("data/table.csv")
    report = resource.index(postgresql_url, table_name="index")
    result = engine.execute("SELECT * FROM index")
    assert report.valid
    assert list(result) == [
        (1, "english"),
        (2, "中国人"),
    ]
