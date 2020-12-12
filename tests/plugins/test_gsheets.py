import os
import pytest
from frictionless import Table, FrictionlessException


# Parser


@pytest.mark.vcr
def test_gsheets_parser():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.vcr
def test_gsheets_parser_with_gid():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit#gid=960698813"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["2", "中国人"], ["3", "german"]]


@pytest.mark.vcr
def test_gsheets_parser_bad_url():
    table = Table("https://docs.google.com/spreadsheets/d/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note.count("404 Client Error: Not Found for url")


@pytest.mark.ci
def test_gsheets_parser_write(credentials):
    path = "https://docs.google.com/spreadsheets/d/1F2OiYmaf8e3x7jSc95_uNgfUyBlSXrcRg-4K_MFNZQI/edit"

    # Write
    with Table("data/table.csv") as table:
        table.write(path, dialect={"credentials": credentials})

    # Read
    with Table(path) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


# Fixtures


@pytest.fixture
def credentials():
    if not os.path.isfile(".google.json"):
        pytest.skip('Environment for "Google Sheets" is not available')
    return ".google.json"
