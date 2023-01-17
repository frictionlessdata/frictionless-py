import pytest
from frictionless import Resource, Dialect, FrictionlessException


# General


def test_dialect():
    dialect = Dialect()
    assert dialect.header_rows == [1]
    assert dialect.header_join == " "
    assert dialect.header_case == True


def test_dialect_bad_property():
    with pytest.raises(FrictionlessException) as excinfo:
        Dialect.from_descriptor({"headerRows": "bad"})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "dialect-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "dialect-error"
    assert reasons[0].note == "'bad' is not of type 'array' at property 'headerRows'"


# Blank Rows


@pytest.mark.parametrize(
    "path",
    [
        "data/blank-rows.csv",
        "data/blank-rows-multiple.csv",
        "data/blank-rows-no-fields.csv",
    ],
)
def test_dialect_skip_blank_rows(path):
    dialect = Dialect(skip_blank_rows=True)
    with Resource(path, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"id": 1101, "name": "John", "age": 30},
            {"id": 1102, "name": "Julie", "age": 26},
        ]
