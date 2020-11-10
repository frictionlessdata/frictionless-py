from frictionless import Row, Field, Schema, extract


# General


def test_basic():
    row = create_row([1, 2, 3])
    assert row.field_positions == [1, 2, 3]
    assert row.row_position == 1
    assert row.row_number == 1
    assert row.blank_cells == {}
    assert row.error_cells == {}
    assert row.errors == []
    assert row == {"field1": 1, "field2": 2, "field3": 3}


# Import/Export


def test_to_dict_with_json_null_values_issue_519():
    source = "text://value\n2020-01-01\n\n2020-03-03"
    process = lambda row: row.to_dict(json=True)
    data = extract(source, format="csv", process=process)
    assert data == [
        {"value": "2020-01-01"},
        {"value": None},
        {"value": "2020-03-03"},
    ]


def test_to_list_with_json_null_values_issue_519():
    source = "text://value\n2020-01-01\n\n2020-03-03"
    process = lambda row: row.to_list(json=True)
    data = extract(source, format="csv", process=process)
    assert data == [
        ["2020-01-01"],
        [None],
        ["2020-03-03"],
    ]


# Helpers


def create_row(cells, *, schema=None, field_positions=[], row_position=1, row_number=1):
    field_positions = field_positions or list(range(1, len(cells) + 1))
    if not schema:
        fields = []
        for field_position in field_positions:
            fields.append(Field({"name": "field%s" % field_position, "type": "any"}))
        schema = Schema({"fields": fields})
    return Row(
        cells,
        schema=schema,
        field_positions=field_positions,
        row_position=row_position,
        row_number=row_number,
    )
