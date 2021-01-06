import pytest
from frictionless import File, helpers


# General


BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/%s"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_file():
    with File("data/table.csv") as file:
        assert file.path == "data/table.csv"
        assert file.source == "data/table.csv"
        assert file.scheme == "file"
        assert file.format == "csv"
        assert file.encoding == "utf-8"
        assert file.innerpath == ""
        assert file.compression == ""
        assert file.read_text() == "id,name\n1,english\n2,中国人\n"
        assert file.stats == {
            "hash": "6c2c61dd9b0e9c6876139a449ed87933",
            "bytes": 30,
            "fields": 0,
            "rows": 0,
        }
