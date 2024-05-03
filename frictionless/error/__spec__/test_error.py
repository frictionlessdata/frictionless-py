from frictionless import Error

# From exception


def test_error():
    error = Error(note="note")
    assert error.type == "error"
    assert error.tags == []
    assert error.note == "note"
    assert error.message == "note"
