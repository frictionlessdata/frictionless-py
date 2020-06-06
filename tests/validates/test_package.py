import json
import pathlib
from goodtables import validate


# General


def test_validate():
    report = validate({'resources': [{'path': 'data/table.csv'}]})
    assert report['valid']


def test_validate_from_path():
    report = validate('data/package/datapackage.json')
    assert report['valid']


def test_validate_from_zip():
    report = validate('data/package.zip', source_type='package')
    assert report['valid']


def test_validate_from_dict():
    with open('data/invalid/datapackage.json') as file:
        report = validate(json.load(file), base_path='data/invalid')
        assert report['errorCount'] == 2


def test_validate_with_non_tabular():
    report = validate(
        {'resources': [{'path': 'data/table.csv'}, {'path': 'data/file.txt'}]}
    )
    assert report['valid']


def test_validate_invalid_descriptor_path():
    report = validate('bad/datapackage.json')
    assert report.flatten(['code', 'details']) == [
        ['package-error', 'Unable to load JSON at "bad/datapackage.json"']
    ]


def test_validate_invalid_package():
    report = validate({'resources': [{'path': 'data/table.csv', 'schema': 'bad'}]})
    assert report.flatten(['code', 'details']) == [
        ['package-error', 'Not resolved Local URI "bad" for resource.schema']
    ]


def test_validate_invalid_package_strict():
    report = validate({'resources': [{'path': 'data/table.csv'}]}, strict=True)
    assert report.flatten(['code', 'details']) == [
        [
            'package-error',
            'Descriptor validation error: {\'path\': \'data/table.csv\', \'profile\': \'data-resource\'} is not valid under any of the given schemas at "resources/0" in descriptor and at "properties/resources/items/oneOf" in profile',
        ]
    ]


def test_validate_invalid_table():
    report = validate({'resources': [{'path': 'data/invalid.csv'}]})
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


def test_validate_pathlib_source():
    report = validate(pathlib.Path('data/package/datapackage.json'))
    assert report['valid']


def test_validate_package_infer():
    report = validate('data/infer/datapackage.json')
    assert report['valid']


def test_validate_package_dialect_header_false():
    descriptor = {
        'resources': [
            {
                'name': 'name',
                'data': [['John', '22'], ['Alex', '33'], ['Paul', '44']],
                'schema': {
                    'fields': [{'name': 'name'}, {'name': 'age', 'type': 'integer'}]
                },
                'dialect': {'header': False},
            }
        ]
    }
    report = validate(descriptor)
    assert report['valid']


# Issues


def test_validate_package_mixed_issue_170():
    report = validate('data/infer/datapackage.json')
    assert report['valid']


def test_validate_package_invalid_json_issue_192():
    report = validate('data/invalid.json', source_type='package')
    assert report.flatten(['code', 'details']) == [
        [
            'package-error',
            'Unable to parse JSON at "data/invalid.json". Expecting property name enclosed in double quotes: line 2 column 5 (char 6)',
        ]
    ]


def test_validate_geopoint_required_constraint_issue_231():
    # We check here that it doesn't raise exceptions
    report = validate('data/geopoint/datapackage.json')
    assert not report['valid']


def test_validate_package_number_test_issue_232():
    # We check here that it doesn't raise exceptions
    report = validate('data/number/datapackage.json')
    assert not report['valid']


def test_validate_package_with_schema_issue_348():
    descriptor = {
        'resources': [
            {
                'name': 'people',
                'data': [
                    ['id', 'name', 'surname'],
                    ['p1', 'Tom', 'Hanks'],
                    ['p2', 'Meryl', 'Streep'],
                ],
                'schema': {
                    'fields': [
                        {'name': 'id', 'type': 'string'},
                        {'name': 'name', 'type': 'string'},
                        {'name': 'surname', 'type': 'string'},
                        {'name': 'dob', 'type': 'date'},
                    ]
                },
            }
        ]
    }
    report1 = validate(descriptor, pick_errors=['#structure'])
    assert report1['valid']
    # TODO: enable
    #  report2 = validate(descriptor)
    #  assert report2.flatten(['rowPosition', 'fieldPosition', 'code']) == [
    #  [None, 4, 'missing-header'],
    #  ]
