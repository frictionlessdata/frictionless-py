import pytest
import textwrap
from importlib import import_module
from frictionless import Field


# General


DESCRIPTOR = {
    "name": "id",
    "type": "integer",
    "format": "default",
    "missingValues": ["-"],
    "constraints": {"required": True},
}


def test_field():
    field = Field.from_descriptor(DESCRIPTOR)
    assert field.name == "id"
    assert field.type == "integer"
    assert field.format == "default"
    assert field.missing_values == ["-"]
    assert field.constraints == {"required": True}
    assert field.required is True


def test_field_defaults():
    field = Field.from_descriptor({"name": "id", "type": "any"})
    assert field.name == "id"
    assert field.type == "any"
    assert field.format == "default"
    assert field.missing_values == [""]
    assert field.constraints == {}
    assert field.required is False


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_field_standard_specs_properties(create_descriptor):
    helpers = import_module("frictionless.helpers")
    options = dict(
        name="name",
        title="title",
        description="description",
        type="string",
        format="default",
        missing_values=["na"],
        constraints={},
        rdf_type="rdf",
    )
    field = (
        Field(**options)
        if not create_descriptor
        else Field.from_descriptor(helpers.create_descriptor(**options))
    )
    assert field.name == "name"
    assert field.title == "title"
    assert field.description == "description"
    assert field.type == "string"
    assert field.format == "default"
    assert field.missing_values == ["na"]
    assert field.constraints == {}
    assert field.rdf_type == "rdf"


def test_field_description_html():
    field = Field(description="**test**")
    assert field.description == "**test**"
    assert field.description_html == "<p><strong>test</strong></p>"


def test_field_description_html_multiline():
    field = Field(description="**test**\n\nline")
    assert field.description == "**test**\n\nline"
    assert field.description_html == "<p><strong>test</strong></p><p>line</p>"


def test_field_description_html_not_set():
    field = Field()
    assert field.description is None
    assert field.description_html == ""


def test_field_description_text():
    field = Field(description="**test**\n\nline")
    assert field.description == "**test**\n\nline"
    assert field.description_text == "test line"


def test_field_description_text_plain():
    field = Field(description="It's just a plain text. Another sentence")
    assert field.description == "It's just a plain text. Another sentence"
    assert field.description_text == "It's just a plain text. Another sentence"


def test_field_pprint():
    field = Field.from_descriptor(
        {
            "name": "name",
            "type": "string",
            "constraints": {"maxLength": 2},
        }
    )
    expected = """
    {'name': 'name', 'type': 'string', 'constraints': {'maxLength': 2}}
    """
    assert repr(field) == textwrap.dedent(expected).strip()


@pytest.mark.parametrize("example_value", [(None), ("42"), ("foo")])
def test_field_with_example_set(example_value):
    field = Field.from_descriptor(
        {
            "name": "name",
            "type": "string",
            "example": example_value,
        }
    )
    assert field.example == example_value
