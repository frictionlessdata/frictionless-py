import tabulator
from goodtables import errors


# From exception


def test_error_from_exception():
    exception = tabulator.exceptions.SourceError('message')
    error = errors.Error.from_exception(exception)
    assert error['code'] == 'source-error'
