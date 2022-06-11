from frictionless import Resource, Checklist, checks


# General


def test_validate_deviated_value():
    source = [["temperature"], [1], [-2], [7], [0], [1], [2], [5], [-4], [100], [8], [3]]
    resource = Resource(source)
    checklist = Checklist(
        checks=[
            checks.deviated_value(
                field_name="temperature",
                average="median",
                interval=3,
            )
        ]
    )
    report = resource.validate(checklist)
    assert report.flatten(["code", "note"]) == [
        [
            "deviated-value",
            'value "100" in row at position "10" and field "temperature" is deviated "[-87.21, 91.21]"',
        ],
    ]


def test_value_deviated_value_not_enough_data():
    source = [
        ["temperature"],
        [1],
    ]
    resource = Resource(source)
    checklist = Checklist(
        {"checks": [{"code": "deviated-value", "fieldName": "temperature"}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_value_not_a_number():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    checklist = Checklist({"checks": [{"code": "deviated-value", "fieldName": "name"}]})
    resource = Resource(source)
    report = resource.validate(checklist)
    assert report.flatten(["code", "note"]) == [
        ["check-error", 'deviated value check requires field "name" to be numeric'],
    ]


def test_validate_deviated_value_non_existent_field():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    checklist = Checklist({"checks": [{"code": "deviated-value", "fieldName": "bad"}]})
    resource = Resource(source)
    report = resource.validate(checklist)
    assert report.flatten(["code", "note"]) == [
        ["check-error", 'deviated value check requires field "bad" to exist'],
    ]


def test_validate_deviated_value_incorrect_average():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    resource = Resource(source)
    checklist = Checklist(
        {
            "checks": [
                {"code": "deviated-value", "fieldName": "row", "average": "bad"},
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["code", "note"]) == [
        [
            "check-error",
            'deviated value check supports only average functions "mean, median, mode"',
        ],
    ]
