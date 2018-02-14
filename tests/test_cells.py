import pytest
import goodtables.cells


class TestCells(object):
    def test_create_header_cells(self):
        # Header cells are cells that have no value
        # (The value becomes the header's value)
        headers = [
            'name',
            'value',
        ]
        schema_fields = [
            'name_schema',
            'value_schema',
        ]

        cells = goodtables.cells.create_cells(headers, schema_fields)
        expected_cells = [
            goodtables.cells.create_cell('name', 'name', 'name_schema', 1),
            goodtables.cells.create_cell('value', 'value', 'value_schema', 2),
        ]

        assert cells == expected_cells

    def test_create_cells_with_values(self):
        headers = [
            'name',
            'value',
        ]
        schema_fields = [
            'name_schema',
            'value_schema',
        ]
        values = [
            'Jane',
            51,
        ]

        cells = goodtables.cells.create_cells(headers, schema_fields, values)
        expected_cells = [
            goodtables.cells.create_cell('name', 'Jane', 'name_schema', 1),
            goodtables.cells.create_cell('value', 51, 'value_schema', 2),
        ]

        assert cells == [dict(cell) for cell in expected_cells]

    def test_create_cells_with_incomplete_values(self):
        headers = [
            'name',
            'value',
        ]
        schema_fields = [
            'name_schema',
            'value_schema',
        ]
        values = [
            'Jane',
        ]

        cells = goodtables.cells.create_cells(headers, schema_fields, values)
        expected_cells = [
            goodtables.cells.create_cell('name', 'Jane', 'name_schema', 1),
            goodtables.cells.create_cell('value', None, 'value_schema', 2),
        ]

        assert cells == [dict(cell) for cell in expected_cells]

    def test_create_cells_with_none_values(self):
        # These happen when loading data from a ODS file with empty cells.
        headers = [
            'name',
            'value',
        ]
        schema_fields = [
            'name_schema',
            'value_schema',
        ]
        values = [
            None,
            51,
        ]

        cells = goodtables.cells.create_cells(headers, schema_fields, values)
        expected_cells = [
            goodtables.cells.create_cell('name', '', 'name_schema', 1),
            goodtables.cells.create_cell('value', 51, 'value_schema', 2),
        ]

        assert cells == [dict(cell) for cell in expected_cells]

    def test_dict_has_expected_keys(self, cell):
        expected_keys = [
            'header',
            'field',
            'value',
            'number',  # FIXME: Remove deprecated "number"
            'column-number',
            'row-number',
        ]

        assert sorted(list(dict(cell).keys())) == sorted(expected_keys)

    def test_dict_removes_none_values(self):
        header = None
        field = None
        value = 'value'
        cell = goodtables.cells.create_cell(header, value, field)

        assert dict(cell) == {'value': cell['value']}


@pytest.fixture
def cell():
    return goodtables.cells.create_cell(
        'header',
        'value',
        'field',
        1,
        1
    )
