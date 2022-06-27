from frictionless import Field


# General

DESCRIPTOR = {
    "name": "id",
    "type": "integer",
    "format": "default",
    "missingValues": ["-"],
    "constraints": {"required": True},
}


def test_field_read_cell():
    field = Field.from_descriptor(DESCRIPTOR)
    assert field.read_cell("1") == (1, None)
    assert field.read_cell("string") == (None, {"type": 'type is "integer/default"'})
    assert field.read_cell("-") == (None, {"required": 'constraint "required" is "True"'})


def test_field_read_cell_string_missing_values():
    field = Field.from_descriptor(
        {
            "name": "name",
            "type": "string",
            "missingValues": ["", "NA", "N/A"],
        }
    )
    assert field.read_cell("") == (None, None)
    assert field.read_cell("NA") == (None, None)
    assert field.read_cell("N/A") == (None, None)


def test_field_read_cell_number_missingValues():
    field = Field.from_descriptor(
        {
            "name": "name",
            "type": "number",
            "missingValues": ["", "NA", "N/A"],
        }
    )
    assert field.read_cell("") == (None, None)
    assert field.read_cell("NA") == (None, None)
    assert field.read_cell("N/A") == (None, None)
