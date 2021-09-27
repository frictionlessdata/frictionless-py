import pytest
from frictionless import Field, helpers


# General


DESCRIPTOR = {
    "name": "id",
    "type": "integer",
    "format": "default",
    "missingValues": ["-"],
    "constraints": {"required": True},
}


def test_field():
    field = Field(DESCRIPTOR)
    assert field.name == "id"
    assert field.type == "integer"
    assert field.format == "default"
    assert field.missing_values == ["-"]
    assert field.constraints == {"required": True}
    assert field.required is True


def test_field_defaults():
    field = Field({"name": "id"})
    assert field.name == "id"
    assert field.type == "any"
    assert field.format == "default"
    assert field.missing_values == [""]
    assert field.constraints == {}
    assert field.required is False


def test_field_read_cell():
    field = Field(DESCRIPTOR)
    assert field.read_cell("1") == (1, None)
    assert field.read_cell("string") == (
        None,
        {"type": 'type is "integer/default"'},
    )
    assert field.read_cell("-") == (None, {"required": 'constraint "required" is "True"'})


def test_field_read_cell_string_missing_values():
    field = Field({"name": "name", "type": "string", "missingValues": ["", "NA", "N/A"]})
    assert field.read_cell("") == (None, None)
    assert field.read_cell("NA") == (None, None)
    assert field.read_cell("N/A") == (None, None)


def test_field_read_cell_number_missingValues():
    field = Field({"name": "name", "type": "number", "missingValues": ["", "NA", "N/A"]})
    assert field.read_cell("") == (None, None)
    assert field.read_cell("NA") == (None, None)
    assert field.read_cell("N/A") == (None, None)


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_field_standard_specs_properties(create_descriptor):
    options = dict(
        name="name",
        title="title",
        description="description",
        type="string",
        format="format",
        missing_values="missing",
        constraints={},
        rdf_type="rdf",
    )
    field = (
        Field(**options)
        if not create_descriptor
        else Field(helpers.create_descriptor(**options))
    )
    assert field.name == "name"
    assert field.title == "title"
    assert field.description == "description"
    assert field.type == "string"
    assert field.format == "format"
    assert field.missing_values == "missing"
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
    assert field.description == ""
    assert field.description_html == ""


def test_field_description_text():
    field = Field(description="**test**\n\nline")
    assert field.description == "**test**\n\nline"
    assert field.description_text == "test line"


def test_field_description_text_plain():
    field = Field(description="It's just a plain text. Another sentence")
    assert field.description == "It's just a plain text. Another sentence"
    assert field.description_text == "It's just a plain text. Another sentence"


# Constraints


@pytest.mark.parametrize(
    "constraints, type, valid",
    [
        # minLength constraint (applies to collections (string, array, object))
        ({"minLength": 4}, "any", False),
        ({"minLength": 4}, "array", True),
        ({"minLength": 4}, "boolean", False),
        ({"minLength": 4}, "date", False),
        ({"minLength": 4}, "datetime", False),
        ({"minLength": 4}, "duration", False),
        ({"minLength": 4}, "geojson", False),
        ({"minLength": 4}, "geopoint", False),
        ({"minLength": 4}, "integer", False),
        ({"minLength": 4}, "number", False),
        ({"minLength": 4}, "object", True),
        ({"minLength": 4}, "string", True),
        ({"minLength": 4}, "time", False),
        ({"minLength": 4}, "year", False),
        ({"minLength": 4}, "yearmonth", False),
        # maxLength constraint (applies to collections (string, array, object))
        ({"maxLength": 3}, "any", False),
        ({"maxLength": 3}, "array", True),
        ({"maxLength": 3}, "boolean", False),
        ({"maxLength": 3}, "date", False),
        ({"maxLength": 3}, "datetime", False),
        ({"maxLength": 3}, "duration", False),
        ({"maxLength": 3}, "geojson", False),
        ({"maxLength": 3}, "geopoint", False),
        ({"maxLength": 3}, "integer", False),
        ({"maxLength": 3}, "number", False),
        ({"maxLength": 3}, "object", True),
        ({"maxLength": 3}, "string", True),
        ({"maxLength": 3}, "time", False),
        ({"maxLength": 3}, "year", False),
        ({"maxLength": 3}, "yearmonth", False),
        # minimum constraint (applies to integer, number, date, time, datetime, year, yearmonth)
        ({"minimum": 4}, "any", False),
        ({"minimum": 4}, "array", False),
        ({"minimum": 4}, "boolean", False),
        ({"minimum": "1789-07-14"}, "date", True),
        ({"minimum": "1789-07-14T08:00:00Z"}, "datetime", True),
        ({"minimum": 4}, "duration", False),
        ({"minimum": 4}, "geojson", False),
        ({"minimum": 4}, "geopoint", False),
        ({"minimum": 4}, "integer", True),
        ({"minimum": 4}, "number", True),
        ({"minimum": 4}, "object", False),
        ({"minimum": 4}, "string", False),
        ({"minimum": "07:07:07"}, "time", True),
        ({"minimum": 4}, "year", True),
        ({"minimum": "1789-07"}, "yearmonth", True),
        # maximum constraint (applies to integer, number, date, time and datetime, year, yearmonth)
        ({"maximum": 4}, "any", False),
        ({"maximum": 4}, "array", False),
        ({"maximum": 4}, "boolean", False),
        ({"maximum": "2001-01-01"}, "date", True),
        ({"maximum": "2001-01-01T12:00:00Z"}, "datetime", True),
        ({"maximum": 4}, "duration", False),
        ({"maximum": 4}, "geojson", False),
        ({"maximum": 4}, "geopoint", False),
        ({"maximum": 4}, "integer", True),
        ({"maximum": 4}, "number", True),
        ({"maximum": 4}, "object", False),
        ({"maximum": 4}, "string", False),
        ({"maximum": "08:09:10"}, "time", True),
        ({"maximum": 4}, "year", True),
        ({"maximum": "2001-01"}, "yearmonth", True),
        # pattern constraint (apply to string)
        ({"pattern": "[0-9]+"}, "any", False),
        ({"pattern": "[0-9]+"}, "array", False),
        ({"pattern": "[0-9]+"}, "boolean", False),
        ({"pattern": "[0-9]+"}, "date", False),
        ({"pattern": "[0-9]+"}, "datetime", False),
        ({"pattern": "[0-9]+"}, "duration", False),
        ({"pattern": "[0-9]+"}, "geojson", False),
        ({"pattern": "[0-9]+"}, "geopoint", False),
        ({"pattern": "[0-9]+"}, "integer", False),
        ({"pattern": "[0-9]+"}, "number", False),
        ({"pattern": "[0-9]+"}, "object", False),
        ({"pattern": "[0-9]+"}, "string", True),
        ({"pattern": "[0-9]+"}, "time", False),
        ({"pattern": "[0-9]+"}, "year", False),
        ({"pattern": "[0-9]+"}, "yearmonth", False),
    ],
)
def test_field_constraint_field_type(constraints, type, valid):
    field = Field({"name": "field", "constraints": constraints, "type": type})
    assert field.metadata_valid == valid


def test_field_read_cell_required():
    field = Field(
        {
            "name": "name",
            "type": "string",
            "constraints": {"required": True},
            "missingValues": ["", "NA", "N/A"],
        }
    )
    read = field.read_cell
    assert read("test") == ("test", None)
    assert read("null") == ("null", None)
    assert read("none") == ("none", None)
    assert read("nil") == ("nil", None)
    assert read("nan") == ("nan", None)
    assert read("-") == ("-", None)
    assert read("NA") == (None, {"required": 'constraint "required" is "True"'})
    assert read("N/A") == (None, {"required": 'constraint "required" is "True"'})
    assert read("") == (None, {"required": 'constraint "required" is "True"'})
    assert read(None) == (None, {"required": 'constraint "required" is "True"'})


def test_field_read_cell_minLength():
    field = Field({"name": "name", "type": "string", "constraints": {"minLength": 2}})
    read = field.read_cell
    assert read("abc") == ("abc", None)
    assert read("ab") == ("ab", None)
    assert read("a") == ("a", {"minLength": 'constraint "minLength" is "2"'})
    # Null value passes
    assert read("") == (None, None)


def test_field_read_cell_maxLength():
    field = Field({"name": "name", "type": "string", "constraints": {"maxLength": 2}})
    read = field.read_cell
    assert read("abc") == ("abc", {"maxLength": 'constraint "maxLength" is "2"'})
    assert read("ab") == ("ab", None)
    assert read("a") == ("a", None)
    # Null value passes
    assert read("") == (None, None)


def test_field_read_cell_minimum():
    field = Field({"name": "name", "type": "integer", "constraints": {"minimum": 2}})
    read = field.read_cell
    assert read("3") == (3, None)
    assert read(3) == (3, None)
    assert read("2") == (2, None)
    assert read(2) == (2, None)
    assert read("1") == (1, {"minimum": 'constraint "minimum" is "2"'})
    assert read(1) == (1, {"minimum": 'constraint "minimum" is "2"'})
    # Null value passes
    assert read("") == (None, None)


def test_field_read_cell_maximum():
    field = Field({"name": "name", "type": "integer", "constraints": {"maximum": 2}})
    read = field.read_cell
    assert read("3") == (3, {"maximum": 'constraint "maximum" is "2"'})
    assert read(3) == (3, {"maximum": 'constraint "maximum" is "2"'})
    assert read("2") == (2, None)
    assert read(2) == (2, None)
    assert read("1") == (1, None)
    assert read(1) == (1, None)
    # Null value passes
    assert read("") == (None, None)


def test_field_read_cell_pattern():
    field = Field({"name": "name", "type": "string", "constraints": {"pattern": "a|b"}})
    read = field.read_cell
    assert read("a") == ("a", None)
    assert read("b") == ("b", None)
    assert read("c") == ("c", {"pattern": 'constraint "pattern" is "a|b"'})
    # Null value passes
    assert read("") == (None, None)


def test_field_read_cell_enum():
    field = Field(
        {"name": "name", "type": "integer", "constraints": {"enum": ["1", "2", "3"]}}
    )
    read = field.read_cell
    assert read("1") == (1, None)
    assert read(1) == (1, None)
    assert read("4") == (4, {"enum": "constraint \"enum\" is \"['1', '2', '3']\""})
    assert read(4) == (4, {"enum": "constraint \"enum\" is \"['1', '2', '3']\""})
    # Null value passes
    assert read("") == (None, None)


def test_field_read_cell_multiple_constraints():
    field = Field(
        {
            "name": "name",
            "type": "string",
            "constraints": {"pattern": "a|b", "enum": ["a", "b"]},
        }
    )
    read = field.read_cell
    assert read("a") == ("a", None)
    assert read("b") == ("b", None)
    assert read("c") == (
        "c",
        {
            "pattern": 'constraint "pattern" is "a|b"',
            "enum": "constraint \"enum\" is \"['a', 'b']\"",
        },
    )
    # Null value passes
    assert read("") == (None, None)


# Import/Export


def test_field_to_copy():
    source = Field(type="integer")
    target = source.to_copy()
    assert source is not target
    assert source == target
