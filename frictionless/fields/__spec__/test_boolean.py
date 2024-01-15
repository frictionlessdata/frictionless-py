import pytest

from frictionless import Field, Schema
from frictionless.resources.table import TableResource

# General


@pytest.mark.parametrize(
    "format, source, target, options",
    [
        ("default", True, True, {}),
        ("default", "true", True, {}),
        ("default", "True", True, {}),
        ("default", "TRUE", True, {}),
        ("default", "1", True, {}),
        ("default", "yes", True, {"trueValues": ["yes"]}),
        ("default", False, False, {}),
        ("default", "false", False, {}),
        ("default", "False", False, {}),
        ("default", "FALSE", False, {}),
        ("default", "0", False, {}),
        ("default", "no", False, {"falseValues": ["no"]}),
        ("default", "t", None, {}),
        ("default", "YES", None, {}),
        ("default", "f", None, {}),
        ("default", "NO", None, {}),
        ("default", "No", None, {}),
        ("default", 0, None, {}),
        ("default", 1, None, {}),
        ("default", "0", False, {"falseValues": ["0"], "trueValues": ["1"]}),
        ("default", "1", True, {"falseValues": ["0"], "trueValues": ["1"]}),
        ("default", "3.14", None, {}),
        ("default", "", None, {}),
        ("default", "Yes", None, {"trueValues": ["yes"]}),
        ("default", "true", None, {"trueValues": ["yes"]}),
        ("default", "No", None, {"falseValues": ["no"]}),
        ("default", "false", None, {"falseValues": ["no"]}),
    ],
)
def test_boolean_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "boolean", "format": format}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    cell, notes = field.read_cell(source)
    assert cell == target


@pytest.mark.parametrize(
    "source, target, options",
    [
        (True, True, {}),
        ("true", True, {}),
        ("True", True, {}),
        ("TRUE", True, {}),
        ("1", True, {}),
        (True, True, {"trueValues": ["yes"]}),
        ("yes", True, {"trueValues": ["yes"]}),
        (False, False, {}),
        ("false", False, {}),
        ("False", False, {}),
        ("FALSE", False, {}),
        ("0", False, {}),
        (False, False, {"falseValues": ["no"]}),
        ("no", False, {"falseValues": ["no"]}),
        ("yes", None, {}),
        ("no", None, {}),
        (0, None, {}),
        (1, None, {}),
        ("YES", None, {}),
        ("NO", None, {}),
        ("", None, {}),
        ("Yes", None, {"trueValues": ["yes"]}),
        ("true", None, {"trueValues": ["yes"]}),
        ("True", None, {"trueValues": ["yes"]}),
        ("TRUE", None, {"trueValues": ["yes"]}),
        ("1", None, {"trueValues": ["yes"]}),
        ("No", None, {"falseValues": ["no"]}),
        ("false", None, {"falseValues": ["no"]}),
        ("False", None, {"falseValues": ["no"]}),
        ("FALSE", None, {"falseValues": ["no"]}),
        ("0", None, {"falseValues": ["no"]}),
    ],
)
def test_boolean_from_schema_descriptor_read_cell(source, target, options):
    schema_descriptor = {"fields": [{"name": "IsTrue", "type": "boolean"}]}
    schema_descriptor["fields"][0].update(options)
    schema = Schema.from_descriptor(schema_descriptor)
    fields = schema.fields
    cell, notes = fields[0].read_cell(source)
    assert cell == target


def test_boolean_from_schema_descriptor_with_example_fix_issue_1610():
    schema_descriptor = {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {
                "name": "IsTrue",
                "type": "boolean",
                "trueValues": ["yes"],
                "falseValues": ["no"],
                "example": "no"
            }
        ]
    }
    
    schema = Schema.from_descriptor(schema_descriptor)
    fields = schema.fields
    source = "yes"
    cell, notes = fields[0].read_cell(source)
    assert cell
 