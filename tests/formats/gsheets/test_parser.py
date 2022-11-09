import pytest
from frictionless import Resource, FrictionlessException, formats


# We don't use VCR for this module testing because
# HTTP requests can contain secrets from Google Credentials. Consider using:
# https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request


# Read


@pytest.mark.ci
def test_gsheets_parser():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing"
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.ci
def test_gsheets_parser_with_gid():
    source = "https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit#gid=960698813"
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
            {"id": 3, "name": "german"},
        ]


@pytest.mark.ci
def test_gsheets_parser_bad_url():
    resource = Resource("https://docs.google.com/spreadsheets/d/bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("404 Client Error: Not Found for url")


# Write


@pytest.mark.skip
@pytest.mark.ci
def test_gsheets_parser_write(google_credentials_path):
    path = "https://docs.google.com/spreadsheets/d/1F2OiYmaf8e3x7jSc95_uNgfUyBlSXrcRg-4K_MFNZQI/edit"
    control = formats.GsheetsControl(credentials=google_credentials_path)
    source = Resource("data/table.csv")
    target = source.write(path, control=control)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
