from goodtables import Row


# Helpers


def create_row(cells, *, column_names=[], line_number=1, row_number=1):
    return Row(
        cells, line_number=line_number, row_number=row_number, column_names=column_names,
    )


# General


def test_basic():
    row = create_row([1, 2, 3])
    assert row.cells == [1, 2, 3]
    assert row.line_number == 1
    assert row.row_number == 1
    assert row.column_names == ['column1', 'column2', 'column3']
    assert row == {'column1': 1, 'column2': 2, 'column3': 3}
