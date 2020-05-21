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
