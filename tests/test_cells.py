import pytest
import goodtables.cells

class MockField(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, MockField):
            return self.name == other.name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

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
        optional_fields = []

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields)
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
        optional_fields = []

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields, values)
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
        optional_fields = []

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields, values)
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
        optional_fields = []

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields, values)
        expected_cells = [
            goodtables.cells.create_cell('name', None, 'name_schema', 1),
            goodtables.cells.create_cell('value', 51, 'value_schema', 2),
        ]

        assert cells == [dict(cell) for cell in expected_cells]

    def test_create_cell_for_optional_field_that_is_present(self):
        headers = [
            'header1',
            'header2'
        ]
        schema_fields = [
            MockField('header1'),
            MockField('header2')
        ]
        optional_fields = ['header2']

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields)
        expected_cells = [
            goodtables.cells.create_cell('header1', 'header1', MockField('header1'), 1),
            goodtables.cells.create_cell('header2', 'header2', MockField('header2'), 2)
        ]

        assert cells == expected_cells

    def test_cell_not_created_for_optional_value_that_is_not_present(self):
        headers = [
            'header1',
        ]
        schema_fields = [
            MockField('header1'),
            MockField('header2')
        ]
        optional_fields = ['header2']

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields)
        expected_cells = [
            goodtables.cells.create_cell('header1', 'header1', MockField('header1'), 1),
        ]

        assert cells == expected_cells
        
    def test_cell_created_when_field_in_schema_but_is_not_optional(self):
        headers = [
            'header1',
        ]
        schema_fields = [
            MockField('header1'),
            MockField('header2')
        ]
        optional_fields = []

        cells = goodtables.cells.create_cells(headers, schema_fields, optional_fields)
        expected_cells = [
            goodtables.cells.create_cell('header1', 'header1', MockField('header1'), 1),
            goodtables.cells.create_cell(None, None, MockField('header2'), 2)
        ]

        assert cells == expected_cells

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
