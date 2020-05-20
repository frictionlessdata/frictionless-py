from goodtables import validate


# General


def test_validate():
    report = validate({'path': 'data/table.csv'})
    print(report)
    assert report['valid']


def test_validate_invalid():
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
