import pathlib
from goodtables import validate


# General


def test_validate():
    report = validate('data/table.csv')
    assert report['valid']


def test_validate_invalid():
    report = validate('data/invalid.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
        [2, 4, 'missing-cell'],
        [3, 3, 'missing-cell'],
        [3, 4, 'missing-cell'],
        [4, None, 'blank-row'],
        [5, 5, 'extra-cell'],
    ]


def test_validate_invalid_error_limit():
    report = validate('data/invalid.csv', error_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
    ]


def test_validate_invalid_row_limit():
    report = validate('data/invalid.csv', row_limit=2)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
        [2, 4, 'missing-cell'],
        [3, 3, 'missing-cell'],
        [3, 4, 'missing-cell'],
    ]


def test_validate_invalid_scheme():
    report = validate('bad://data/table.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'scheme-error'],
    ]


def test_validate_invalid_format():
    report = validate('data/table.bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'format-error'],
    ]


def test_validate_invalid_schema():
    source = [['name', 'age'], ['Alex', '33']]
    schema = {'fields': [{'name': 'name'}, {'name': 'age', 'type': 'bad'}]}
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


def test_validate_duplicate_headers():
    report = validate('data/duplicate-headers.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'duplicate-header'],
        [None, 5, 'duplicate-header'],
    ]


def test_validate_defective_rows():
    report = validate('data/defective-rows.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, 3, 'missing-cell'],
        [3, 4, 'extra-cell'],
    ]


def test_validate_blank_rows():
    report = validate('data/blank-rows.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
    ]


def test_validate_blank_rows_multiple():
    report = validate('data/blank-rows-multiple.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
        [5, None, 'blank-row'],
        [6, None, 'blank-row'],
        [7, None, 'blank-row'],
        [8, None, 'blank-row'],
        [9, None, 'blank-row'],
        [10, None, 'blank-row'],
        [11, None, 'blank-row'],
        [12, None, 'blank-row'],
        [13, None, 'blank-row'],
        [14, None, 'blank-row'],
    ]


def test_validate_structure_errors_with_error_limit():
    report = validate('data/structure-errors.csv', error_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
        [5, 4, 'extra-cell'],
        [5, 5, 'extra-cell'],
    ]


def test_validate_structure_errors_with_row_limit():
    report = validate('data/structure-errors.csv', row_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
    ]


def test_validate_blank_headers():
    report = validate('data/blank-headers.csv', row_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 2, 'blank-header'],
    ]


def test_validate_blank_cell_not_required():
    report = validate('data/blank-cells.csv')
    assert report['valid']


def test_validate_schema_invalid_json():
    report = validate('data/table.csv', schema='data/invalid.json')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


# Report props


def test_validate_report_props():
    report = validate('data/table.csv')
    assert report['valid'] is True
    assert report['warnings'] == []
    assert report.table['valid'] is True
    assert report.table['source'] == 'data/table.csv'
    assert report.table['headers'] == ['id', 'name']
    assert report.table['scheme'] == 'file'
    assert report.table['format'] == 'csv'
    assert report.table['encoding'] == 'utf-8'
    assert report.table['dialect'] == {}
    assert report.table['rowCount'] == 2
    assert report.table['errors'] == []
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'id', 'type': 'integer'},
            {'format': 'default', 'name': 'name', 'type': 'string'},
        ],
        'missingValues': [''],
    }


# Source as pathlib.Path


def test_source_pathlib_path_table():
    report = validate(pathlib.Path('data/table.csv'))
    assert report['valid']


# Catch exceptions


def test_validate_catch_all_open_exceptions():
    report = validate('data/latin1.csv', encoding='utf-8')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'encoding-error'],
    ]


def test_validate_catch_all_iter_exceptions():
    # Reducing sample size to get raise on iter, not on open
    report = validate([['h'], [1], 'bad'], sample_size=1)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'source-error'],
    ]


# Not data/headers/rows source


def test_validate_no_data():
    report = validate('data/empty.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'source-error', 'There are no data available'],
    ]


def test_validate_no_headers():
    report = validate('data/empty-headers.csv', headers=None)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'source-error', 'There are no headers available'],
    ]


def test_validate_no_rows():
    report = validate('data/empty-rows.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'source-error', 'There are no rows available'],
    ]


# Issues


def test_validate_fails_with_wrong_encoding_issue_274():
    # For now, by default encoding is detected incorectly by chardet
    report = validate('data/encoding-274.csv', encoding='utf-8')
    assert report['valid']


def test_validate_invalid_table_schema_issue_304():
    source = [['name', 'age'], ['Alex', '33']]
    schema = {'fields': [{'name': 'name'}, {'name': 'age', 'type': 'bad'}]}
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


def test_validate_missing_local_file_raises_loading_error_issue_315():
    report = validate('bad-path.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'loading-error'],
    ]


def test_validate_inline_no_format_issue_349():
    with open('data/table.csv', 'rb') as source:
        report = validate(source)
        assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
            [None, None, 'format-error', 'Format "None" is not supported'],
        ]


def test_validate_inline_not_a_binary_issue_349():
    with open('data/table.csv') as source:
        report = validate(source)
        assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
            [None, None, 'source-error', 'Only byte streams are supported.'],
        ]
