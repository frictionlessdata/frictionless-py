import pytest
from frictionless import Table, FrictionlessException


# We don't use VCR for this module testing because
# HTTP requests can contain secrets from Google Credentials. Consider using:
# https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request


# Parser


@pytest.mark.ci
def test_gsheets_parser():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.ci
def test_gsheets_parser_with_gid():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit#gid=960698813"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["2", "中国人"], ["3", "german"]]


@pytest.mark.ci
def test_gsheets_parser_bad_url():
    table = Table("https://docs.google.com/spreadsheets/d/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note.count("404 Client Error: Not Found for url")


@pytest.mark.ci
def test_gsheets_parser_write(google_credentials_path):
    path = "https://docs.google.com/spreadsheets/d/1F2OiYmaf8e3x7jSc95_uNgfUyBlSXrcRg-4K_MFNZQI/edit"

    # Write
    with Table("data/table.csv") as table:
        table.write(path, dialect={"credentials": google_credentials_path})

    # Read
    with Table(path) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
