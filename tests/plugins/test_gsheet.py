import pytest
from frictionless import Table, FrictionlessException


# Parser


@pytest.mark.ci
def test_table_gsheet():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.ci
def test_table_gsheet_with_gid():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit#gid=960698813"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["2", "中国人"], ["3", "german"]]


@pytest.mark.ci
def test_table_gsheet_bad_url():
    table = Table("https://docs.google.com/spreadsheets/d/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note.count("404 Client Error: Not Found for url")
