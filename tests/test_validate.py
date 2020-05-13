import pytest
import pathlib
from goodtables import validate


# General


def test_validate_valid():
    report = validate('data/valid.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []


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


def test_validate_invalid_schema():
    source = [['name', 'age'], ['Alex', '33']]
    schema = {'fields': [{'name': 'name'}, {'name': 'age', 'type': 'bad'}]}
    report = validate(source, schema=schema)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'schema-error'],
    ]


# Report props


def test_validate_report_props():
    report = validate('data/valid.csv')
    assert report['valid'] is True
    assert report['warnings'] == []
    assert report.table['valid'] is True
    assert report.table['source'] == 'data/valid.csv'
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
    report = validate(pathlib.Path('data/valid.csv'))
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []


@pytest.mark.skip
def test_source_pathlib_path_datapackage():
    report = validate(pathlib.Path('data/datapackages/valid/datapackage.json'))
    assert report['table-count'] == 2
    assert report['valid']
