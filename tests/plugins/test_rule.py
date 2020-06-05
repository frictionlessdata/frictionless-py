from goodtables import validate


# Blacklisted Value


def test_validate_blacklisted_value():
    report = validate(
        'data/table.csv',
        extra_checks=[('rule/blacklisted-value', {'fieldName': 'id', 'blacklist': [2]})],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, 1, 'rule/blacklisted-value'],
    ]


def test_validate_blacklisted_value_task_error():
    report = validate(
        'data/table.csv',
        extra_checks=[('rule/blacklisted-value', {'fieldName': 'bad', 'blacklist': [2]})],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'task-error'],
    ]


def test_validate_blacklisted_value_many_rules():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
        [3, 'John'],
        [4, 'mistake'],
        [5, 'error'],
        [6],
    ]
    report = validate(
        source,
        extra_checks=[
            ('rule/blacklisted-value', {'fieldName': 'row', 'blacklist': [10]}),
            ('rule/blacklisted-value', {'fieldName': 'name', 'blacklist': ['mistake']}),
            ('rule/blacklisted-value', {'fieldName': 'row', 'blacklist': [10]}),
            ('rule/blacklisted-value', {'fieldName': 'name', 'blacklist': ['error']}),
        ],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, 2, 'rule/blacklisted-value'],
        [5, 2, 'rule/blacklisted-value'],
        [6, 2, 'missing-cell'],
    ]


def test_validate_blacklisted_value_many_rules_with_non_existent_field():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source,
        extra_checks=[
            ('rule/blacklisted-value', {'fieldName': 'row', 'blacklist': [10]}),
            ('rule/blacklisted-value', {'fieldName': 'bad', 'blacklist': ['mistake']},),
        ],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'task-error'],
    ]


# Sequential Value


def test_validate_sequential_value():
    source = [
        ['row', 'index2', 'index3'],
        [2, 1, 1],
        [3, 2, 3],
        [4, 3, 5],
        [5, 5, 6],
        [6],
    ]
    report = validate(
        source,
        extra_checks=[
            ('rule/sequential-value', {'fieldName': 'index2'}),
            ('rule/sequential-value', {'fieldName': 'index3'}),
        ],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [3, 3, 'rule/sequential-value'],
        [5, 2, 'rule/sequential-value'],
        [6, 2, 'missing-cell'],
        [6, 3, 'missing-cell'],
    ]


def test_validate_sequential_value_non_existent_field():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
        [3, 'Brad'],
    ]
    report = validate(
        source,
        extra_checks=[
            ('rule/sequential-value', {'column': 'row'}),
            ('rule/sequential-value', {'column': 'bad'}),
        ],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [None, None, 'task-error'],
    ]


# Custom constraint


def test_validate_custom_constraint():
    source = [
        ['row', 'salary', 'bonus'],
        [2, 1000, 200],
        [3, 2500, 500],
        [4, 1300, 500],
        [5, 5000, 1000],
        [6],
    ]
    report = validate(
        source,
        extra_checks=[('rule/custom-constraint', {'constraint': 'salary == bonus * 5'})],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'rule/custom-constraint'],
        [6, 2, 'missing-cell'],
        [6, 3, 'missing-cell'],
        [6, None, 'rule/custom-constraint'],
    ]


def test_validate_custom_constraint_incorrect_constraint():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source,
        extra_checks=[
            ('rule/custom-constraint', {'constraint': 'vars()'}),
            ('rule/custom-constraint', {'constraint': 'import(os)'}),
            ('rule/custom-constraint', {'constraint': 'non_existent > 0'}),
        ],
    )
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, None, 'rule/custom-constraint'],
        [2, None, 'rule/custom-constraint'],
        [2, None, 'rule/custom-constraint'],
    ]
