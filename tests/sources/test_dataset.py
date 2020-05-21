from goodtables import validate


# General


def test_validate():
    report = validate([{'source': 'data/table.csv'}])
    assert report['valid']


def test_validate_multiple():
    report = validate([{'source': 'data/table.csv'}, {'source': 'data/matrix.csv'}])
    assert report['valid']


def test_validate_multiple_invalid():
    report = validate([{'source': 'data/table.csv'}, {'source': 'data/invalid.csv'}])
    assert report.flatten(['tableNumber', 'rowPosition', 'fieldPosition', 'code']) == [
        [2, None, 3, 'blank-header'],
        [2, None, 4, 'duplicate-header'],
        [2, 2, 3, 'missing-cell'],
        [2, 2, 4, 'missing-cell'],
        [2, 3, 3, 'missing-cell'],
        [2, 3, 4, 'missing-cell'],
        [2, 4, None, 'blank-row'],
        [2, 5, 5, 'extra-cell'],
    ]


def test_validate_multiple_invalid_with_schema():
    report = validate(
        [
            {
                'source': 'data/table.csv',
                'schema': {'fields': [{'name': 'bad'}, {'name': 'name'}]},
            },
            {'source': 'data/invalid.csv'},
        ],
    )
    assert report.flatten(['tableNumber', 'rowPosition', 'fieldPosition', 'code']) == [
        [1, None, 1, 'non-matching-header'],
        [2, None, 3, 'blank-header'],
        [2, None, 4, 'duplicate-header'],
        [2, 2, 3, 'missing-cell'],
        [2, 2, 4, 'missing-cell'],
        [2, 3, 3, 'missing-cell'],
        [2, 3, 4, 'missing-cell'],
        [2, 4, None, 'blank-row'],
        [2, 5, 5, 'extra-cell'],
    ]


def test_validate_with_datapackage():
    report = validate([{'source': 'data/valid/datapackage.json'}])
    assert report['valid']
