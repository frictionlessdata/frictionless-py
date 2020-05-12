from tableschema import Field
from goodtables import Row


# General


def test_basic():
    row = create_row([1, 2, 3])
    assert row.field_positions == [1, 2, 3]
    assert row.row_position == 1
    assert row.row_number == 1
    assert row.blank_cells == {}
    assert row.error_cells == {}
    assert row.errors == []
    assert row == {'field1': 1, 'field2': 2, 'field3': 3}


# Helpers


def create_row(cells, *, fields=[], field_positions=[], row_position=1, row_number=1):
    field_positions = field_positions or list(range(1, len(cells) + 1))
    if not fields:
        for field_position in field_positions:
            fields.append(Field({'name': 'field%s' % field_position, 'type': 'any'}))
    return Row(
        cells,
        fields=fields,
        field_positions=field_positions,
        row_position=row_position,
        row_number=row_number,
    )
