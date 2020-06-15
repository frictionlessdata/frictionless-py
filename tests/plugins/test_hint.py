from goodtables import validate


# Duplicate Row


def test_validate_duplicate_row():
    report = validate('data/duplicate-rows.csv', extra_checks=['hint/duplicate-row'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [4, None, 'hint/duplicate-row'],
    ]


def test_validate_duplicate_row_valid():
    report = validate('data/table.csv', extra_checks=['hint/duplicate-row'])
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []


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
                'hint/deviated-value',
                {'fieldName': 'temperature', 'average': 'median', 'interval': 3},
            ),
        ],
    )
    assert report.flatten(['code', 'note']) == [
        [
            'hint/deviated-value',
            'value "100" in row at position "10" and field "temperature" is deviated "[-87.21, 91.21]"',
        ],
    ]


def test_value_deviated_value_not_enough_data():
    source = [
        ['temperature'],
        [1],
    ]
    report = validate(
        source, extra_checks=[('hint/deviated-value', {'fieldName': 'temperature'})]
    )
    assert report.flatten(['code', 'note']) == []


def test_validate_deviated_value_not_a_number():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source, extra_checks=[('hint/deviated-value', {'fieldName': 'name'})]
    )
    assert report.flatten(['code', 'note']) == [
        ['task-error', 'deviated value check requires field "name" to be numiric'],
    ]


def test_validate_deviated_value_non_existent_field():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source, extra_checks=[('hint/deviated-value', {'fieldName': 'bad'})],
    )
    assert report.flatten(['code', 'note']) == [
        ['task-error', 'deviated value check requires field "bad" to exist'],
    ]


def test_validate_deviated_value_incorrect_average():
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(
        source,
        extra_checks=[('hint/deviated-value', {'fieldName': 'row', 'average': 'bad'})],
    )
    assert report.flatten(['code', 'note']) == [
        [
            'task-error',
            'deviated value check supports only average functions "mean, median, mode"',
        ],
    ]


# Truncated value


def test_validate_truncated_values():
    source = [
        ['int', 'str'],
        ['a' * 255, 32767],
        ['good', 2147483647],
    ]
    report = validate(source, extra_checks=['hint/truncated-value'],)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == [
        [2, 1, 'hint/truncated-value'],
        [2, 2, 'hint/truncated-value'],
        [3, 2, 'hint/truncated-value'],
    ]


def test_validate_truncated_values_close_to_errors():
    source = [
        ['int', 'str'],
        ['a' * 254, 32766],
        ['good', 2147483646],
    ]
    report = validate(source, extra_checks=['hint/truncated-value'],)
    assert report.flatten(['rowPosition', 'fieldPosition', 'code']) == []
