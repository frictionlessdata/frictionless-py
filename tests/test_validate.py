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


# Report


def test_validate_report():
    report = validate('data/valid.csv')
    assert report['valid'] is True
    assert report['warnings'] == []
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []
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
