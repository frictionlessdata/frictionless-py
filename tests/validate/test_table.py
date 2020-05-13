from goodtables import validate_table


# General


def test_validate_table_valid():
    report = validate_table('data/valid.csv')
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []


def test_validate_table_invalid():
    report = validate_table('data/invalid.csv')
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
