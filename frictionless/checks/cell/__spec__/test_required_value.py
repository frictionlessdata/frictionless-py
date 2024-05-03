from datetime import datetime

from frictionless import Checklist, Resource, checks

# General


def test_validate_required_value_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="name", values=["Alex", "Alisha"])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_not_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="name", values=["Alexx"])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == [
        [
            "required-value",
            'Required values not found: The value "Alexx" is required to be present in '
            'field "name" in at least one row.',
        ]
    ]


def test_validate_required_value_multiple_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="name", values=["Alex", "Alisha"])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_multiple_not_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="name", values=["Alexx", "Alishaa"])]
    )
    report = resource.validate(checklist)
    # order of result changes so flattening the result into set
    responses = {error[0] for error in report.flatten(["message"])}
    assert responses == {
        'Required values not found: The value "Alexx" is required to be present in field "name" in at least one row.',
        'Required values not found: The value "Alishaa" is required to be present in field "name" in at least one row.',
    }


def test_validate_required_value_fields_not_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="test", values=["Alex"])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == [
        [
            "check-error",
            'Check is not valid: required value check requires field "test" to exist',
        ]
    ]


def test_validate_required_value_multiple_fields_not_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="test", values=["Alex", "Alisha"])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == [
        [
            "check-error",
            'Check is not valid: required value check requires field "test" to exist',
        ]
    ]


def test_validate_required_value_multiple_fields_one_not_found():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(
        checks=[checks.required_value(field_name="name", values=["Alexx", "Alisha"])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == [
        [
            "required-value",
            'Required values not found: The value "Alexx" is required to be present in '
            'field "name" in at least one row.',
        ]
    ]


def test_validate_required_value_found_integer():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist(checks=[checks.required_value(field_name="age", values=[21])])
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_boolean():
    resource = Resource(
        [
            ["name", "age", "student"],
            ["Alex", 33, False],
            ["Alisha", 20, True],
            ["Alexa", 21, True],
        ]
    )
    checklist = Checklist(
        checks=[checks.required_value(field_name="student", values=[True])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_float():
    resource = Resource(
        [
            ["name", "age", "student", "amount_paid"],
            ["Alex", 33, False, 100.0],
            ["Alisha", 20, True, 10.0],
            ["Alexa", 21, True, 10.0],
        ]
    )
    checklist = Checklist(
        checks=[checks.required_value(field_name="amount_paid", values=[10.0])]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_datetime():
    resource = Resource(
        [
            ["name", "age", "student", "amount_paid", "date_of_registration"],
            ["Alex", 33, False, 100.0, "2010-02-01T12:00:00Z"],
            ["Alisha", 20, True, 10.0, "2011-01-03T12:00:00Z"],
            ["Alexa", 21, True, 10.0, "2020-01-01T12:00:00Z"],
        ]
    )
    checklist = Checklist(
        checks=[
            checks.required_value(
                field_name="date_of_registration",
                values=[datetime.strptime("2020-01-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")],
            )
        ]
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_descriptor():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "name",
                    "values": ["Alex", "Alisha"],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_not_found_descriptor():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "name",
                    "values": ["Alexx"],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == [
        [
            "required-value",
            'Required values not found: The value "Alexx" is required to be present in '
            'field "name" in at least one row.',
        ]
    ]


def test_validate_required_value_field_not_found_descriptor():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "test",
                    "values": ["Alex"],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == [
        [
            "check-error",
            'Check is not valid: required value check requires field "test" to exist',
        ]
    ]


def test_validate_required_value_found_integer_descriptor():
    resource = Resource([["name", "age"], ["Alex", 33], ["Alisha", 20], ["Alexa", 21]])
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "age",
                    "values": [21],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_boolean_descriptor():
    resource = Resource(
        [
            ["name", "age", "student"],
            ["Alex", 33, False],
            ["Alisha", 20, True],
            ["Alexa", 21, True],
        ]
    )
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "student",
                    "values": [True],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_float_descriptor():
    resource = Resource(
        [
            ["name", "age", "student", "amount_paid"],
            ["Alex", 33, False, 100.0],
            ["Alisha", 20, True, 10.0],
            ["Alexa", 21, True, 10.0],
        ]
    )
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "amount_paid",
                    "values": [100.0],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []


def test_validate_required_value_found_datetime_descriptor():
    resource = Resource(
        [
            ["name", "age", "student", "amount_paid", "date_of_registration"],
            ["Alex", 33, False, 100.0, "2010-02-01T12:00:00Z"],
            ["Alisha", 20, True, 10.0, "2011-01-03T12:00:00Z"],
            ["Alexa", 21, True, 10.0, "2020-01-01T12:00:00Z"],
        ]
    )
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {
                    "type": "required-value",
                    "fieldName": "date_of_registration",
                    "values": [
                        datetime.strptime("2020-01-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
                    ],
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "message"]) == []
