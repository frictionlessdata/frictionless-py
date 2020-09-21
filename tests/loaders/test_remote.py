import pytest
from frictionless import Table

BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/%s"


# Read


@pytest.mark.ci
def test_table_https():
    with Table(BASE_URL % "data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.ci
def test_table_https_latin1():
    # Github returns wrong encoding `utf-8`
    with Table(BASE_URL % "data/special/latin1.csv") as table:
        assert table.read_data()
