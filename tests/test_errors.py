from frictionless import errors


# From exception


def test_error_from_exception():
    error = errors.SourceError(note="note")
    assert error["code"] == "source-error"
