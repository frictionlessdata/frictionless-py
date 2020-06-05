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


# Truncated value


def test_validate_truncated_values():
    source = [
        ['int', 'str'],
        ['a' * 255, 32767],
        ['good', 2147483647],
    ]
    report = validate(source, extra_checks=['prob/truncated-value'],)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, 1, 'prob/truncated-value'],
        [2, 2, 'prob/truncated-value'],
        [3, 2, 'prob/truncated-value'],
    ]


def test_validate_truncated_values_close_to_errors():
    source = [
        ['int', 'str'],
        ['a' * 254, 32766],
        ['good', 2147483646],
    ]
    report = validate(source, extra_checks=['prob/truncated-value'],)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []
