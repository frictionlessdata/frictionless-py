from goodtables import validate


# Deviated Value


def test_validate_deviated_value():
    source = [
        ['temperature'],
        [1],
        [-2],
        [7],
        [0],
        [1],
        [2],
        [5],
        [-4],
        [100],
        [8],
        [3],
    ]
    report = validate(
        source,
        extra_checks=[
            (
                'prob/deviated-value',
                {'fieldName': 'temperature', 'average': 'median', 'interval': 3},
            ),
        ],
    )
    assert report.flatten(['rowNumber', 'fieldName', 'code']) == [
        [9, 'temperature', 'prob/deviated-value'],
    ]


def test_value_deviated_value_not_enough_data():
    source = [
        ['temperature'],
        [1],
    ]
    report = validate(
        source, extra_checks=[('prob/deviated-value', {'fieldName': 'temperature'})]
    )
    assert report.flatten(['rowNumber', 'fieldName', 'code']) == []


def test_validate_deviated_value_not_a_number():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source, extra_checks=[('prob/deviated-value', {'fieldName': 'name'})]
    )
    assert report.flatten(['rowNumber', 'fieldName', 'code']) == [
        [1, 'name', 'type-error'],
    ]


def test_validate_deviated_value_non_existent_field():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source, extra_checks=[('prob/deviated-value', {'fieldName': 'non-existent'})],
    )
    assert report.flatten(['rowNumber', 'fieldName', 'code']) == [
        [None, None, 'task-error'],
    ]


def test_validate_deviated_value_incorrect_average():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source,
        extra_checks=[('prob/deviated-value', {'fieldName': 'name', 'average': 'bad'})],
    )
    assert report.flatten(['rowNumber', 'fieldName', 'code']) == [
        [None, None, 'task-error'],
    ]
