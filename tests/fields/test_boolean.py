import pytest

from frictionless import Field

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
        ("default", "No", None, {"falseValues": ["no"]}),
    ],
)
def test_boolean_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "boolean", "format": format}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    cell, notes = field.read_cell(source)
    assert cell == target
