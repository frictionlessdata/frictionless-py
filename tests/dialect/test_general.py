import pytest
from frictionless import Dialect, FrictionlessException


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
