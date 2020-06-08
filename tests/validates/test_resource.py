from goodtables import validate


# General


def test_validate():
    report = validate({'path': 'data/table.csv'})
    assert report.valid


def test_validate_invalid_source():
    report = validate('bad.json')
    assert report.flatten(['code', 'details']) == [
        ['resource-error', 'Unable to load JSON at "bad.json"']
    ]


def test_validate_invalid_resource():
    report = validate({'path': 'data/table.csv', 'schema': 'bad'})
    assert report.flatten(['code', 'details']) == [
        ['resource-error', 'Not resolved Local URI "bad" for resource.schema']
    ]


def test_validate_invalid_resource_strict():
    report = validate({'path': 'data/table.csv'}, strict=True)
    assert report.flatten(['code', 'details']) == [
        [
            'resource-error',
            'Descriptor validation error: {\'path\': \'data/table.csv\', \'profile\': \'data-resource\'} is not valid under any of the given schemas at "" in descriptor and at "oneOf" in profile',
        ]
    ]


def test_validate_invalid_table():
    report = validate({'path': 'data/invalid.csv'})
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
