import pytest
import pathlib
from tableschema import infer
from goodtables import validate, Check, errors


# General


def test_validate():
    report = validate('data/table.csv')
    assert report.valid


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
    assert report.valid


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


def test_validate_task_error():
    report = validate('data/table.csv', limit_rows='bad')
    assert report.flatten(['code', 'details']) == [
        [
            'task-error',
            '"\'bad\' is not of type \'number\', \'null\'" at "tables/0/limitRows" in metadata and at "properties/tables/items/properties/limitRows/type" in profile',
        ],
    ]


# Source


def test_validate_source_invalid():
    # Reducing sample size to get raise on iter, not on open
    report = validate([['h'], [1], 'bad'], infer_sample=1)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'source-error'],
    ]


def test_validate_source_pathlib_path_table():
    report = validate(pathlib.Path('data/table.csv'))
    assert report.valid


def test_validate_scheme():
    report = validate('data/table.csv', scheme='file')
    assert report.valid


def test_validate_scheme_invalid():
    report = validate('bad://data/table.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'scheme-error'],
    ]


def test_validate_format():
    report = validate('data/table.csv', format='csv')
    assert report.valid


def test_validate_format_invalid():
    report = validate('data/table.bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'format-error'],
    ]


def test_validate_encoding():
    report = validate('data/table.csv', encoding='utf-8')
    assert report.valid


def test_validate_encoding_invalid():
    report = validate('data/latin1.csv', encoding='utf-8')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'encoding-error'],
    ]


def test_validate_compression():
    report = validate('data/table.csv.zip')
    assert report.valid


def test_validate_compression_explicit():
    report = validate('data/table.csv.zip', compression='zip')
    assert report.valid


def test_validate_compression_invalid():
    report = validate('data/table.csv.zip', compression='bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'compression-error'],
    ]


# Headers


def test_validate_headers_row_none():
    report = validate('data/without-headers.csv', headers_row=None)
    assert report.valid
    assert report.table.row_count == 3
    assert report.table['headers'] is None


def test_validate_headers_row_none_extra_cell():
    report = validate('data/without-headers-extra.csv', headers_row=None)
    assert report.table.row_count == 3
    assert report.table['headers'] is None
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, 3, 'extra-cell'],
    ]


def test_validate_headers_row_number():
    report = validate('data/matrix.csv', headers_row=2)
    assert report.table['headers'] == ['11', '12', '13', '14']
    assert report.valid


def test_validate_headers_row_list_of_numbers():
    report = validate('data/matrix.csv', headers_row=[2, 3, 4])
    assert report.table['headers'] == ['11 21 31', '12 22 32', '13 23 33', '14 24 34']
    assert report.valid


def test_validate_headers_row_list_of_numbers_and_headers_joiner():
    report = validate('data/matrix.csv', headers_row=[2, 3, 4], headers_joiner='.')
    assert report.table['headers'] == ['11.21.31', '12.22.32', '13.23.33', '14.24.34']
    assert report.valid


# Fields


def test_validate_pick_fields():
    report = validate('data/matrix.csv', pick_fields=[2, 'f3'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_pick_fields_regex():
    report = validate('data/matrix.csv', pick_fields=['<regex>f[23]'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_skip_fields():
    report = validate('data/matrix.csv', skip_fields=[1, 'f4'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_skip_fields_regex():
    report = validate('data/matrix.csv', skip_fields=['<regex>f[14]'])
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_limit_fields():
    report = validate('data/matrix.csv', limit_fields=1)
    assert report.table['headers'] == ['f1']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_offset_fields():
    report = validate('data/matrix.csv', offset_fields=3)
    assert report.table['headers'] == ['f4']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


def test_validate_limit_and_offset_fields():
    report = validate('data/matrix.csv', limit_fields=2, offset_fields=1)
    assert report.table['headers'] == ['f2', 'f3']
    assert report.table['rowCount'] == 4
    assert report.table['valid']


# Rows


def test_validate_pick_rows():
    report = validate('data/matrix.csv', pick_rows=[1, 3, '31'])
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_pick_rows_regex():
    report = validate('data/matrix.csv', pick_rows=['<regex>[f23]1'])
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_skip_rows():
    report = validate('data/matrix.csv', skip_rows=[2, '41'])
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_skip_rows_regex():
    report = validate('data/matrix.csv', skip_rows=['<regex>[14]1'])
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_skip_rows_blank():
    report = validate('data/blank-rows.csv', skip_rows=['<blank>'])
    assert report.table['headers'] == ['id', 'name', 'age']
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


def test_validate_limit_rows():
    report = validate('data/matrix.csv', limit_rows=1)
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 1
    assert report.table['valid']


def test_validate_offset_rows():
    report = validate('data/matrix.csv', offset_rows=3)
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 1
    assert report.table['valid']


def test_validate_limit_and_offset_rows():
    report = validate('data/matrix.csv', limit_rows=2, offset_rows=1)
    assert report.table['headers'] == ['f1', 'f2', 'f3', 'f4']
    assert report.table['rowCount'] == 2
    assert report.table['valid']


def test_validate_invalid_limit_rows():
    report = validate('data/invalid.csv', limit_rows=2)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
        [2, 4, 'missing-cell'],
        [3, 3, 'missing-cell'],
        [3, 4, 'missing-cell'],
    ]


def test_validate_structure_errors_with_limit_rows():
    report = validate('data/structure-errors.csv', limit_rows=3)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
    ]


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


def test_validate_schema_extra_headers_and_cells():
    schema = {'fields': [{'name': 'id', 'type': 'integer'}]}
    report = validate('data/table.csv', schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 2, 'extra-header'],
        [2, 2, 'extra-cell'],
        [3, 2, 'extra-cell'],
    ]


def test_validate_schema_multiple_errors():
    source = 'data/schema-errors.csv'
    schema = 'data/schema.json'
    report = validate(source, schema=schema, pick_errors=['#schema'], limit_errors=3)
    assert report.table.partial
    assert report.table.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, 1, 'type-error'],
        [4, 2, 'required-error'],
        [4, 3, 'required-error'],
    ]


def test_validate_schema_min_length_constraint():
    source = [['row', 'word'], [2, 'a'], [3, 'ab'], [4, 'abc'], [5, 'abcd'], [6]]
    schema = {
        'fields': [
            {'name': 'row', 'type': 'integer'},
            {'name': 'word', 'type': 'string', 'constraints': {'minLength': 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=['constraint-error'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, 2, 'constraint-error'],
    ]


def test_validate_schema_max_length_constraint():
    source = [['row', 'word'], [2, 'a'], [3, 'ab'], [4, 'abc'], [5, 'abcd'], [6]]
    schema = {
        'fields': [
            {'name': 'row', 'type': 'integer'},
            {'name': 'word', 'type': 'string', 'constraints': {'maxLength': 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=['constraint-error'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, 2, 'constraint-error'],
        [5, 2, 'constraint-error'],
    ]


def test_validate_schema_minimum_constraint():
    source = [['row', 'score'], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = {
        'fields': [
            {'name': 'row', 'type': 'integer'},
            {'name': 'score', 'type': 'integer', 'constraints': {'minimum': 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=['constraint-error'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, 2, 'constraint-error'],
    ]


def test_validate_schema_maximum_constraint():
    source = [['row', 'score'], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = {
        'fields': [
            {'name': 'row', 'type': 'integer'},
            {'name': 'score', 'type': 'integer', 'constraints': {'maximum': 2}},
        ]
    }
    report = validate(source, schema=schema, pick_errors=['constraint-error'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, 2, 'constraint-error'],
        [5, 2, 'constraint-error'],
    ]


def test_validate_sync_schema():
    schema = infer('data/table.csv')
    report = validate('data/sync-schema.csv', schema=schema, sync_schema=True)
    assert report.valid
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'name', 'type': 'string'},
            {'format': 'default', 'name': 'id', 'type': 'integer'},
        ],
        'missingValues': [''],
    }


def test_validate_sync_schema_invalid():
    source = [['LastName', 'FirstName', 'Address'], ['Test', 'Tester', '23 Avenue']]
    schema = {'fields': [{'name': 'id'}, {'name': 'FirstName'}, {'name': 'LastName'}]}
    report = validate(source, schema=schema, sync_schema=True)
    assert report.valid


def test_validate_schema_headers_errors():
    source = [
        ['id', 'last_name', 'first_name', 'language'],
        [1, 'Alex', 'John', 'English'],
        [2, 'Peters', 'John', 'Afrikaans'],
        [3, 'Smith', 'Paul', None],
    ]
    schema = {
        'fields': [
            {'name': 'id', 'type': 'number'},
            {'name': 'language', 'constraints': {'required': True}},
            {'name': 'country'},
        ]
    }
    report = validate(source, schema=schema, sync_schema=True)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, 4, 'required-error'],
    ]


def test_validate_patch_schema():
    patch_schema = {'missingValues': ['-']}
    report = validate('data/table.csv', patch_schema=patch_schema)
    assert report.valid
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'id', 'type': 'integer'},
            {'format': 'default', 'name': 'name', 'type': 'string'},
        ],
        'missingValues': ['-'],
    }


def test_validate_patch_schema_fields():
    patch_schema = {'fields': {'id': {'type': 'string'}}, 'missingValues': ['-']}
    report = validate('data/table.csv', patch_schema=patch_schema)
    assert report.valid
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'id', 'type': 'string'},
            {'format': 'default', 'name': 'name', 'type': 'string'},
        ],
        'missingValues': ['-'],
    }


def test_validate_infer_type_string():
    report = validate('data/table.csv', infer_type='string')
    assert report.valid
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'id', 'type': 'string'},
            {'format': 'default', 'name': 'name', 'type': 'string'},
        ],
        'missingValues': [''],
    }


def test_validate_infer_type_any():
    report = validate('data/table.csv', infer_type='any')
    assert report.valid
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'id', 'type': 'any'},
            {'format': 'default', 'name': 'name', 'type': 'any'},
        ],
        'missingValues': [''],
    }


def test_validate_infer_names():
    report = validate(
        'data/without-headers.csv', headers_row=None, infer_names=['id', 'name']
    )
    assert report.table['headers'] is None
    assert report.table['rowCount'] == 3
    assert report.table['schema']['fields'][0]['name'] == 'id'
    assert report.table['schema']['fields'][1]['name'] == 'name'
    assert report.valid


# Integrity


def test_validate_size():
    report = validate('data/table.csv', size=30)
    assert report.table['valid']


def test_validate_size_invalid():
    report = validate('data/table.csv', size=40)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'size-error', 'expected is "40" and actual is "30"'],
    ]


def test_validate_hash():
    hash = '6c2c61dd9b0e9c6876139a449ed87933'
    report = validate('data/table.csv', hash=hash)
    assert report.table['valid']


def test_validate_hash_invalid():
    hash = '6c2c61dd9b0e9c6876139a449ed87933'
    report = validate('data/table.csv', hash='bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'hash-error', 'expected is "bad" and actual is "%s"' % hash],
    ]


def test_validate_hash_md5():
    hash = 'md5:6c2c61dd9b0e9c6876139a449ed87933'
    report = validate('data/table.csv', hash=hash)
    assert report.table['valid']


def test_validate_hash_md5_invalid():
    hash = '6c2c61dd9b0e9c6876139a449ed87933'
    report = validate('data/table.csv', hash='md5:bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'hash-error', 'expected is "bad" and actual is "%s"' % hash],
    ]


def test_validate_hash_sha1():
    hash = 'sha1:db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e'
    report = validate('data/table.csv', hash=hash)
    assert report.table['valid']


def test_validate_hash_sha1_invalid():
    hash = 'db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e'
    report = validate('data/table.csv', hash='sha1:bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'hash-error', 'expected is "bad" and actual is "%s"' % hash],
    ]


def test_validate_hash_sha256():
    hash = 'sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8'
    report = validate('data/table.csv', hash=hash)
    assert report.table['valid']


def test_validate_hash_sha256_invalid():
    hash = 'a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8'
    report = validate('data/table.csv', hash='sha256:bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'hash-error', 'expected is "bad" and actual is "%s"' % hash],
    ]


def test_validate_hash_sha512():
    hash = 'sha512:d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd'
    report = validate('data/table.csv', hash=hash)
    assert report.table['valid']


def test_validate_hash_sha512_invalid():
    hash = 'd52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd'
    report = validate('data/table.csv', hash='sha512:bad')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code', 'details']) == [
        [None, None, 'hash-error', 'expected is "bad" and actual is "%s"' % hash],
    ]


def test_validate_unique_error():
    report = validate(
        'data/unique-field.csv',
        schema='data/unique-field.json',
        pick_errors=['unique-error'],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [10, 1, 'unique-error'],
    ]


def test_validate_unique_error_and_type_error():
    source = [
        ['id', 'unique_number'],
        ['a1', 100],
        ['a2', 'bad'],
        ['a3', 100],
    ]
    schema = {
        'fields': [
            {'name': 'id'},
            {'name': 'unique_number', 'type': 'number', 'constraints': {'unique': True}},
        ]
    }
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, 2, 'type-error'],
        [4, 2, 'unique-error'],
    ]


def test_validate_primary_key_error():
    report = validate(
        'data/unique-field.csv',
        schema='data/unique-field.json',
        pick_errors=['primary-key-error'],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [10, None, 'primary-key-error'],
    ]


def test_validate_primary_key_and_unique_error():
    report = validate('data/unique-field.csv', schema='data/unique-field.json',)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [10, 1, 'unique-error'],
        [10, None, 'primary-key-error'],
    ]


def test_validate_primary_key_error_composite():
    source = [
        ['id', 'name'],
        [1, 'Alex'],
        [1, 'John'],
        ['', 'Paul'],
        [1, 'John'],
        ['', None],
    ]
    schema = {
        'fields': [
            {'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
        ],
        'primaryKey': ['id', 'name'],
    }
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [5, None, 'primary-key-error'],
        [6, None, 'blank-row'],
        [6, None, 'primary-key-error'],
    ]


def test_validate_foreign_key_error():
    schema = {
        'fields': [
            {'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
        ],
        'foreignKeys': [
            {'fields': 'id', 'reference': {'resource': 'ids', 'fields': 'id'}}
        ],
    }
    lookup = {'ids': {('id',): set([(1,), (2,)])}}
    report = validate('data/table.csv', schema=schema, lookup=lookup)
    assert report.valid


def test_validate_foreign_key_error_invalid():
    schema = {
        'fields': [
            {'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
        ],
        'foreignKeys': [
            {'fields': 'id', 'reference': {'resource': 'ids', 'fields': 'id'}}
        ],
    }
    lookup = {'ids': {('id',): set([(1,)])}}
    report = validate('data/table.csv', schema=schema, lookup=lookup)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, None, 'foreign-key-error'],
    ]


# Validation


def test_validate_pick_errors():
    report = validate('data/invalid.csv', pick_errors=['blank-header', 'blank-row'])
    assert report.table.scope == ['blank-header', 'blank-row']
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [4, None, 'blank-row'],
    ]


def test_validate_pick_errors_tags():
    report = validate('data/invalid.csv', pick_errors=['#head'])
    assert report.table.scope == [
        'extra-header',
        'missing-header',
        'blank-header',
        'duplicate-header',
        'non-matching-header',
    ]
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
    ]


def test_validate_skip_errors():
    report = validate('data/invalid.csv', skip_errors=['blank-header', 'blank-row'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
        [2, 4, 'missing-cell'],
        [3, 3, 'missing-cell'],
        [3, 4, 'missing-cell'],
        [5, 5, 'extra-cell'],
    ]


def test_validate_skip_errors_tags():
    report = validate('data/invalid.csv', skip_errors=['#head'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, 3, 'missing-cell'],
        [2, 4, 'missing-cell'],
        [3, 3, 'missing-cell'],
        [3, 4, 'missing-cell'],
        [4, None, 'blank-row'],
        [5, 5, 'extra-cell'],
    ]


def test_validate_invalid_limit_errors():
    report = validate('data/invalid.csv', limit_errors=3)
    assert report.table.partial
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [2, 3, 'missing-cell'],
    ]


def test_validate_structure_errors_with_limit_errors():
    report = validate('data/structure-errors.csv', limit_errors=3)
    assert report.table.partial
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'blank-row'],
        [5, 4, 'extra-cell'],
        [5, 5, 'extra-cell'],
    ]


def test_validate_extra_checks():

    # Create check
    class ExtraCheck(Check):
        def validate_row(self, row):
            yield errors.BlankRowError(
                details='',
                cells=list(map(str, row.values())),
                row_number=row.row_number,
                row_position=row.row_position,
            )

    # Validate table
    report = validate('data/table.csv', extra_checks=[ExtraCheck])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, None, 'blank-row'],
        [3, None, 'blank-row'],
    ]


def test_validate_extra_checks_with_arguments():

    # Create check
    class ExtraCheck(Check):
        def validate_row(self, row):
            yield errors.BlankRowError(
                details='',
                cells=list(map(str, row.values())),
                row_number=row.row_number,
                row_position=self.get('rowPosition') or row.row_position,
            )

    # Validate table
    extra_checks = [(ExtraCheck, {'rowPosition': 1})]
    report = validate('data/table.csv', extra_checks=extra_checks)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [1, None, 'blank-row'],
        [1, None, 'blank-row'],
    ]


def test_validate_extra_checks_bad_name():
    report = validate('data/table.csv', extra_checks=['bad'])
    assert report.flatten(['code', 'details']) == [
        ['task-error', 'Check name "bad" should be in "plugin/element" form'],
    ]


def test_validate_extra_checks_bad_plugin_name():
    report = validate('data/table.csv', extra_checks=['bad/some-check'])
    assert report.flatten(['code', 'details']) == [
        [
            'task-error',
            'Plugin "bad" is not installed. Run: "pip install goodtables[bad]"',
        ],
    ]


# Issues


def test_composite_primary_key_unique_issue_215():
    source = {
        'resources': [
            {
                'name': 'name',
                'data': [['id1', 'id2'], ['a', '1'], ['a', '2']],
                'schema': {
                    'fields': [{'name': 'id1'}, {'name': 'id2'}],
                    'primaryKey': ['id1', 'id2'],
                },
            }
        ],
    }
    report = validate(source)
    assert report.valid


def test_composite_primary_key_not_unique_issue_215():
    descriptor = {
        'resources': [
            {
                'name': 'name',
                'data': [['id1', 'id2'], ['a', '1'], ['a', '1']],
                'schema': {
                    'fields': [{'name': 'id1'}, {'name': 'id2'}],
                    'primaryKey': ['id1', 'id2'],
                },
            }
        ],
    }
    report = validate(descriptor, skip_errors=['duplicate-row'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, None, 'primary-key-error'],
    ]


def test_validate_infer_fields_issue_223():
    source = [['name1', 'name2'], ['123', 'abc'], ['456', 'def'], ['789', 'ghi']]
    patch_schema = {'fields': {'name': {'type': 'string'}}}
    report = validate(source, patch_schema=patch_schema)
    assert report.valid


def test_validate_infer_fields_issue_225():
    source = [['name1', 'name2'], ['123', None], ['456', None], ['789']]
    patch_schema = {'fields': {'name': {'type': 'string'}}}
    report = validate(source, patch_schema=patch_schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, 2, 'missing-cell'],
    ]


def test_validate_fails_with_wrong_encoding_issue_274():
    # For now, by default encoding is detected incorectly by chardet
    report = validate('data/encoding-issue-274.csv', encoding='utf-8')
    assert report.valid


def test_validate_wide_table_with_order_fields_issue_277():
    source = 'data/issue-277.csv'
    schema = 'data/issue-277.json'
    report = validate(source, schema=schema, sync_schema=True)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [49, 50, 'required-error'],
        [68, 50, 'required-error'],
        [69, 50, 'required-error'],
    ]


def test_validate_invalid_table_schema_issue_304():
    source = [['name', 'age'], ['Alex', '33']]
    schema = {'fields': [{'name': 'name'}, {'name': 'age', 'type': 'bad'}]}
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


def test_validate_table_is_invalid_issue_312():
    report = validate('data/issue-312.xlsx')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, 3, 'blank-header'],
        [None, 4, 'duplicate-header'],
        [None, 5, 'blank-header'],
        [5, None, 'blank-row'],
    ]


def test_validate_order_fields_issue_313():
    source = 'data/issue-313.xlsx'
    pick_fields = [1, 2, 3, 4, 5]
    schema = {
        'fields': [
            {'name': 'Column_1', 'type': 'string'},
            {'name': 'Column_2', 'type': 'string', 'constraints': {'required': True}},
            {'name': 'Column_3', 'type': 'string'},
            {'name': 'Column_4', 'type': 'string'},
            {'name': 'Column_5', 'type': 'string'},
        ]
    }
    report = validate(source, pick_fields=pick_fields, schema=schema, sync_schema=True)
    assert report.valid


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
