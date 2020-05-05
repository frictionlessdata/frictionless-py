from goodtables import Row


# Helpers


def create_row(cells, *, field_names=[], line_number=1, row_number=1):
    return Row(
        cells, field_names=field_names, line_number=line_number, row_number=row_number
    )


# General


def test_basic():
    row = create_row([1, 2, 3])
    assert row.cells == [1, 2, 3]
    assert row.line_number == 1
    assert row.row_number == 1
    assert row.field_names == ['field1', 'field2', 'field3']
    assert row.deletions == {}
    assert row.errors == []
    assert row == {'field1': 1, 'field2': 2, 'field3': 3}
