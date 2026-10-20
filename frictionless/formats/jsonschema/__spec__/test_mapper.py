import json
from pathlib import Path

from frictionless import Schema, validate

# General


def test_jsonschema_mapper_schema_from_jsonschema():
    schema = Schema.from_jsonschema("data/ecrin.json")
    assert schema.to_descriptor() == {
        "fields": [
            {"name": "file_type", "type": "string", "description": "always 'study'"},
            {
                "name": "id",
                "type": "integer",
                "description": "Internal accession number of the study within the MDR database",
                "constraints": {"required": True},
            },
            {
                "name": "display_title",
                "type": "string",
                "description": "By default the public or brief study title. If that is missing then the full scientific title, as used on the protocol document",
                "constraints": {"required": True},
            },
            {
                "name": "brief_description",
                "type": "object",
                "description": "Brief description, usually a few lines, of the study",
            },
            {
                "name": "data_sharing_statement",
                "type": "object",
                "description": "A statement from the sponsor and / or study leads about their intentions for IPD sharing",
            },
            {
                "name": "study_type",
                "type": "object",
                "description": "Categorisation of study type, e.g. 'Interventional', or 'Observational'",
            },
            {
                "name": "study_status",
                "type": "object",
                "description": "Categorisation of study status, e.g. 'Active, not recruiting', or 'Completed'",
            },
            {
                "name": "study_enrolment",
                "type": "integer",
                "description": "The anticipated or actual total number of participants in the clinical study.",
            },
            {
                "name": "study_gender_elig",
                "type": "object",
                "description": "Whether the study is open to all genders, or just male or female",
            },
            {
                "name": "min_age",
                "type": "object",
                "description": "The minimum age, if any, for a study participant",
            },
            {
                "name": "max_age",
                "type": "object",
                "description": "The maximum age, if any, for a study participant",
            },
            {"name": "study_identifiers", "type": "array"},
            {"name": "study_titles", "type": "array"},
            {"name": "study_features", "type": "array"},
            {"name": "study_topics", "type": "array"},
            {"name": "study_relationships", "type": "array"},
            {"name": "linked_data_objects", "type": "array"},
            {
                "name": "provenance_string",
                "type": "string",
                "description": "A listing of the source or sources (usually a trial registry) from which the data for the study has been drawn, and the date-time(s) when the data was last downloaded",
            },
        ]
    }


def test_jsonschema_mapper_maps_string_constraints():
    schema = Schema.from_jsonschema(
        {
            "properties": {
                "name": {"type": "string", "minLength": 5, "maxLength": 10},
            }
        }
    )
    field = schema.get_field("name")
    assert field.type == "string"
    assert field.constraints["minLength"] == 5
    assert field.constraints["maxLength"] == 10


def test_jsonschema_mapper_does_not_map_pattern():
    # JSON Schema's `pattern` is a partial match, Frictionless's is a full
    # match. Carrying it across would report tables the JSON Schema accepts
    # as INVALID, so the mapper leaves it alone.
    schema = Schema.from_jsonschema(
        {"properties": {"name": {"type": "string", "pattern": "a+"}}}
    )
    assert "pattern" not in schema.get_field("name").constraints


def test_jsonschema_mapper_maps_numeric_constraints():
    schema = Schema.from_jsonschema(
        {
            "properties": {
                "age": {"type": "integer", "minimum": 18, "maximum": 65},
                "score": {"type": "number", "minimum": 0, "maximum": 1},
            }
        }
    )
    age = schema.get_field("age")
    assert age.constraints == {"minimum": 18, "maximum": 65}
    score = schema.get_field("score")
    assert score.constraints == {"minimum": 0, "maximum": 1}


def test_jsonschema_mapper_maps_enum():
    schema = Schema.from_jsonschema(
        {"properties": {"status": {"type": "string", "enum": ["open", "closed"]}}}
    )
    field = schema.get_field("status")
    assert field.constraints["enum"] == ["open", "closed"]


def test_jsonschema_mapper_drops_an_enum_the_type_cannot_read():
    # A string field reads each enum value through its own reader, and a
    # reader that cannot read a value returns None. `enum: [1, 2]` would
    # become `enum: [None, None]` and fail every row, so the enum is not
    # carried at all.
    schema = Schema.from_jsonschema(
        {"properties": {"status": {"type": "string", "enum": [1, 2]}}}
    )
    assert "enum" not in schema.get_field("status").constraints


def test_jsonschema_mapper_drops_a_bound_the_type_cannot_read():
    # An integer field reads a bound through its own reader, and a fractional
    # value reads as None. Carrying it would raise a TypeError when the
    # constraint is compared against a cell.
    schema = Schema.from_jsonschema(
        {"properties": {"age": {"type": "integer", "minimum": 1.5}}}
    )
    assert "minimum" not in schema.get_field("age").constraints


def test_jsonschema_mapper_maps_enum_for_a_typeless_property():
    # A property with no type is read by the any field, which reads every
    # value as itself, so an enum it can read is carried.
    schema = Schema.from_jsonschema(
        {"properties": {"status": {"enum": ["open", "closed"]}}}
    )
    assert schema.get_field("status").constraints["enum"] == ["open", "closed"]


def test_jsonschema_mapper_no_spurious_constraints():
    schema = Schema.from_jsonschema(
        {"properties": {"name": {"type": "string"}, "count": {"type": "integer"}}}
    )
    assert schema.get_field("name").constraints == {}
    assert schema.get_field("count").constraints == {}


def test_jsonschema_mapper_constraints_enforced_in_validation(tmp_path, monkeypatch):
    schema = Schema.from_jsonschema(
        {"required": ["name"], "properties": {"name": {"type": "string", "minLength": 5}}}
    )
    # The path has to be inside the working directory (the frictionless
    # path-safety guard), so the table is written inside the temporary
    # directory and the working directory is moved there.
    monkeypatch.chdir(tmp_path)
    Path("table.csv").write_text("name\nab\n", encoding="utf-8")
    report = validate("table.csv", schema=schema)
    assert not report.valid
    messages = [error.message for task in report.tasks for error in task.errors]
    assert any("minLength" in message for message in messages), messages


def test_jsonschema_mapper_enum_enforced_in_validation(tmp_path, monkeypatch):
    schema = Schema.from_jsonschema(
        {"properties": {"status": {"type": "string", "enum": ["open", "closed"]}}}
    )
    monkeypatch.chdir(tmp_path)
    Path("table.csv").write_text("status\nopen\n", encoding="utf-8")
    assert validate("table.csv", schema=schema).valid
    Path("table.csv").write_text("status\narchived\n", encoding="utf-8")
    assert not validate("table.csv", schema=schema).valid


def test_jsonschema_mapper_pattern_is_not_enforced_as_a_full_match(
    tmp_path, monkeypatch
):
    # JSON Schema accepts "ba" and "abc" for the pattern "a+". If the mapper
    # carried the pattern as a full match, both would be reported invalid.
    schema = Schema.from_jsonschema(
        {"properties": {"name": {"type": "string", "pattern": "a+"}}}
    )
    monkeypatch.chdir(tmp_path)
    Path("table.csv").write_text("name\nba\n", encoding="utf-8")
    assert validate("table.csv", schema=schema).valid


def test_jsonschema_mapper_drops_a_numeric_enum_on_a_typeless_property():
    # The any field reads a cell as itself, so a cell from a tabular source
    # (a string) never equals a numeric enum member. Carrying the enum would
    # fail every row of every CSV.
    schema = Schema.from_jsonschema({"properties": {"x": {"enum": [1, 2]}}})
    assert "enum" not in schema.get_field("x").constraints


def test_jsonschema_mapper_carries_an_integral_bound_on_an_integer_field():
    # The integer field reads 2.0 as 2, so the bound is carried.
    schema = Schema.from_jsonschema(
        {"properties": {"n": {"type": "integer", "minimum": 2.0}}}
    )
    assert schema.get_field("n").constraints["minimum"] == 2.0


def test_jsonschema_mapper_maps_array_item_counts():
    # Frictionless checks minLength on an array field with len(cell), which
    # is the item count - the same thing JSON Schema's minItems says.
    schema = Schema.from_jsonschema(
        {"properties": {"tags": {"type": "array", "minItems": 2}}}
    )
    assert schema.get_field("tags").constraints["minLength"] == 2


def test_jsonschema_mapper_maps_object_property_counts():
    schema = Schema.from_jsonschema(
        {"properties": {"meta": {"type": "object", "minProperties": 1}}}
    )
    assert schema.get_field("meta").constraints["minLength"] == 1


def test_jsonschema_mapper_drops_a_negative_length():
    # A negative length is not a length. Carrying it would fail every row.
    schema = Schema.from_jsonschema(
        {"properties": {"name": {"type": "string", "maxLength": -1}}}
    )
    assert "maxLength" not in schema.get_field("name").constraints


def test_jsonschema_mapper_carries_a_boolean_enum():
    schema = Schema.from_jsonschema(
        {"properties": {"ok": {"type": "boolean", "enum": [True, False]}}}
    )
    assert schema.get_field("ok").constraints["enum"] == [True, False]


def test_jsonschema_mapper_array_item_count_enforced(tmp_path, monkeypatch):
    schema = Schema.from_jsonschema(
        {"properties": {"tags": {"type": "array", "minItems": 2}}}
    )
    monkeypatch.chdir(tmp_path)
    Path("table.csv").write_text('tags\n["a"]\n', encoding="utf-8")
    report = validate("table.csv", schema=schema)
    assert not report.valid
    messages = [error.message for task in report.tasks for error in task.errors]
    assert any("minLength" in message for message in messages), messages


def test_jsonschema_mapper_object_property_count_enforced(tmp_path, monkeypatch):
    schema = Schema.from_jsonschema(
        {"properties": {"meta": {"type": "object", "minProperties": 2}}}
    )
    monkeypatch.chdir(tmp_path)
    Path("table.csv").write_text('meta\n"{""a"": 1}"\n', encoding="utf-8")
    report = validate("table.csv", schema=schema)
    assert not report.valid
    messages = [error.message for task in report.tasks for error in task.errors]
    assert any("minLength" in message for message in messages), messages


def test_jsonschema_mapper_typeless_numeric_enum_still_validates(tmp_path, monkeypatch):
    # The numeric enum is not carried, so the table is not failed by it. The
    # point of the rule is that a mistyped schema must not make every row
    # invalid.
    schema = Schema.from_jsonschema({"properties": {"x": {"enum": [1, 2]}}})
    monkeypatch.chdir(tmp_path)
    Path("table.csv").write_text("x\n1\n", encoding="utf-8")
    assert validate("table.csv", schema=schema).valid


def test_jsonschema_mapper_carries_a_bound_the_field_can_read():
    # The field reads "5" as the number 5, so the bound is carried, and the
    # field reads the constraint through its own reader again when it checks
    # a cell. The value is kept as the profile gave it, so the schema stays
    # writable as JSON.
    schema = Schema.from_jsonschema(
        {"properties": {"n": {"type": "integer", "minimum": "5"}}}
    )
    assert schema.get_field("n").constraints["minimum"] == "5"
    field = schema.get_field("n")
    _cell, notes = field.read_cell(7)
    assert notes is None
    _cell, notes = field.read_cell(3)
    assert notes is not None and "minimum" in notes


def test_jsonschema_mapper_produces_a_writable_schema():
    # The schema has to survive being written out: a constraint the number
    # field's reader produced would be a Decimal, and a Decimal cannot be
    # serialized to JSON.
    schema = Schema.from_jsonschema(
        {
            "properties": {
                "x": {"type": "number", "minimum": 0.5, "maximum": 10},
                "n": {"type": "integer", "minimum": 18},
                "s": {"type": "string", "minLength": 5},
                "e": {"type": "string", "enum": ["a", "b"]},
            }
        }
    )
    descriptor = json.loads(schema.to_json())
    assert descriptor["fields"][0]["constraints"]["minimum"] == 0.5
    assert descriptor["fields"][1]["constraints"]["minimum"] == 18


def test_jsonschema_mapper_maps_a_maximum_item_count():
    # A maximum carried as a minimum would report valid tables invalid.
    schema = Schema.from_jsonschema(
        {"properties": {"tags": {"type": "array", "maxItems": 2}}}
    )
    constraints = schema.get_field("tags").constraints
    assert constraints["maxLength"] == 2
    assert "minLength" not in constraints


def test_jsonschema_mapper_maps_a_maximum_property_count():
    schema = Schema.from_jsonschema(
        {"properties": {"meta": {"type": "object", "maxProperties": 3}}}
    )
    constraints = schema.get_field("meta").constraints
    assert constraints["maxLength"] == 3
    assert "minLength" not in constraints
