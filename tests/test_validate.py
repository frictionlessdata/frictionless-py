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


def test_validate_blank_headers():
    report = validate('data/blank-headers.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 2, 'blank-header'],
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


def test_validate_blank_cell_not_required():
    report = validate('data/blank-cells.csv')
    assert report['valid']


def test_validate_no_data():
    report = validate('data/empty.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'source-error', 'There are no rows available'],
    ]


def test_validate_no_rows():
    report = validate('data/without-rows.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'source-error', 'There are no rows available'],
    ]


# Source


def test_validate_source_invalid():
    # Reducing sample size to get raise on iter, not on open
    report = validate([['h'], [1], 'bad'], sample_size=1)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'source-error'],
    ]


def test_validate_source_pathlib_path_table():
    report = validate(pathlib.Path('data/table.csv'))
    assert report['valid']


# Headers


def test_validate_no_headers():
    report = validate('data/without-headers.csv', headers=None)
    assert report['valid']


def test_validate_no_headers_extra_cell():
    report = validate('data/without-headers-extra.csv', headers=None)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, 3, 'extra-cell'],
    ]


# Scheme


def test_validate_scheme():
    report = validate('data/table.csv', scheme='file')
    assert report['valid']


def test_validate_scheme_invalid():
    report = validate('bad://data/table.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'scheme-error'],
    ]


# Format


def test_validate_format():
    report = validate('data/table.csv', format='csv')
    assert report['valid']


def test_validate_format_invalid():
    report = validate('data/table.bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'format-error'],
    ]


# Encoding


def test_validate_encoding():
    report = validate('data/table.csv', encoding='utf-8')
    assert report['valid']


def test_validate_encoding_invalid():
    report = validate('data/latin1.csv', encoding='utf-8')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'encoding-error'],
    ]


# Compression


def test_validate_compression():
    report = validate('data/table.csv.zip')
    assert report['valid']


def test_validate_compression_explicit():
    report = validate('data/table.csv.zip', compression='zip')
    assert report['valid']


def test_validate_compression_invalid():
    report = validate('data/table.csv.zip', compression='bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'compression-error'],
    ]


# Pick|skip fields|rows


def test_validate_pick_fields():
    report = validate('data/matrix.csv', pick_fields=[2, 'f3'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_skip_fields():
    report = validate('data/matrix.csv', skip_fields=[1, 'f4'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_pick_rows():
    report = validate('data/matrix.csv', pick_rows=[1, 3, '31'])
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_skip_rows():
    report = validate('data/matrix.csv', skip_rows=[2, '41'])
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_pick_rows_and_fields():
    report = validate('data/matrix.csv', pick_rows=[1, 3, '31'], pick_fields=[2, 'f3'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_skip_rows_and_fields():
    report = validate('data/matrix.csv', skip_rows=[2, '41'], skip_fields=[1, 'f4'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


# Schema


def test_validate_schema_invalid():
    source = [['name', 'age'], ['Alex', '33']]
    schema = {'fields': [{'name': 'name'}, {'name': 'age', 'type': 'bad'}]}
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


def test_validate_schema_invalid_json():
    report = validate('data/table.csv', schema='data/invalid.json')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


# Row|error limit


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


def test_validate_structure_errors_with_row_limit():
    report = validate('data/structure-errors.csv', row_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
    ]


def test_validate_invalid_error_limit():
    report = validate('data/invalid.csv', error_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
    ]


def test_validate_structure_errors_with_error_limit():
    report = validate('data/structure-errors.csv', error_limit=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
        [5, 4, 'extra-cell'],
        [5, 5, 'extra-cell'],
    ]


# Report


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


# Issues


def test_validate_fails_with_wrong_encoding_issue_274():
    # For now, by default encoding is detected incorectly by chardet
    report = validate('data/encoding-issue-274.csv', encoding='utf-8')
    assert report['valid']


def test_validate_invalid_table_schema_issue_304():
    source = [['name', 'age'], ['Alex', '33']]
    schema = {'fields': [{'name': 'name'}, {'name': 'age', 'type': 'bad'}]}
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


def test_validate_missing_local_file_raises_scheme_error_issue_315():
    report = validate('bad-path.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'scheme-error'],
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
