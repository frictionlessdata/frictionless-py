from goodtables import validate


# General


def test_validate():
    report = validate({'resources': [{'path': 'data/table.csv'}]})
    assert report['valid']


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
