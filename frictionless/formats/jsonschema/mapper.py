from __future__ import annotations

from typing import Any, Dict

from ...schema import Field, Schema
from ...system import Mapper

# JsonSchema keyword -> Frictionless constraint name, per JsonSchema type.
# Frictionless supports different constraints per field type (see
# frictionless/fields/*): string has minLength/maxLength, while
# integer/number have minimum/maximum, and array/object count their
# elements with minLength/maxLength.
#
# The keywords that are not carried are listed in
# docs/formats/jsonschema.md. This comment names only the mapping table
# below; the reasons live in the documentation page and, where a rule is
# local to this file, in the functions that apply it.
CONSTRAINTS_BY_TYPE = {
    "string": {"minLength": "minLength", "maxLength": "maxLength"},
    "integer": {"minimum": "minimum", "maximum": "maximum"},
    "number": {"minimum": "minimum", "maximum": "maximum"},
    "array": {"minItems": "minLength", "maxItems": "maxLength"},
    "object": {"minProperties": "minLength", "maxProperties": "maxLength"},
}

# The JsonSchema keywords whose value is an element count rather than a value
# the field reads. Frictionless checks a length with `len(cell)`, so the
# constraint is a plain non-negative integer and is not read through the
# field's reader: a string field's reader reads a string, not a number, so
# asking it about the length would refuse the very constraint the mapping
# exists for.
COUNT_KEYWORDS = (
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "minProperties",
    "maxProperties",
)


def _read(field: Field, value: Any) -> Any:
    """Read this value the way the field reads a cell, or None.

    Frictionless reads a constraint value through the field's own reader
    before it compares it against a cell (frictionless/schema/field.py), and
    a reader that cannot read a value returns None. So the guard in this
    module is: a value the reader cannot read is a value the constraint
    cannot work with - a bound that compares every cell against None and
    raises a TypeError, or an enum that fails every row.

    Asking the field instead of keeping a table of what each type can read
    means the answer stays right when a field type changes.
    """
    reader = field.create_value_reader()
    try:
        return reader(value)
    except (TypeError, ValueError):
        # A reader that raises on a value it cannot read is still a reader
        # that cannot read it.
        return None


def _is_count(value: Any) -> bool:
    """Is this a usable element count?"""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _carries_enum(field: Field, values: Any) -> bool:
    """Can this field read every one of these enum values?

    A cell is compared against the enum with `in`, and the cell is read
    through the field's own reader first. So the enum values and the cells
    have to be the same kind of value: a string field whose enum is `[1, 2]`
    reads both enum members as None, and every cell then fails the
    constraint - a table where every row is invalid because the schema was
    mistyped. A schema whose enum does not fit its field carries no enum.

    The `any` field is the exception, and the reason is that it has no
    reader of its own: it reads a cell as itself, so a cell from a tabular
    source (a string) never equals a numeric enum member, and a numeric enum
    on a typeless property would fail every row of every such table. A
    typeless property therefore carries an enum only when its members are
    strings, which is the one kind that is the same in a CSV and in a JSON
    source.
    """
    if not isinstance(values, list) or not values:
        return False
    if field.type == "any":
        return all(isinstance(value, str) for value in values)
    return all(_read(field, value) is not None for value in values)


class JsonschemaMapper(Mapper):
    """ERD Mapper"""

    # Write

    def read_schema(self, profile: Dict[str, Any]) -> Schema:  # type: ignore
        schema = Schema()
        required = profile.get("required", [])
        assert isinstance(required, list)
        properties = profile.get("properties", {})
        assert isinstance(properties, dict)
        for name, prop in properties.items():
            assert isinstance(name, str)
            assert isinstance(prop, dict)

            # Type
            type = prop.get("type", "any")
            assert isinstance(type, str)
            if type not in ["string", "integer", "number", "boolean", "object", "array"]:
                type = "any"

            # Field
            field = Field.from_descriptor({"type": type, "name": name})
            schema.add_field(field)

            # Constraints
            # The field is built first, because the field knows what it can
            # read, and a constraint the field cannot read is worse than no
            # constraint at all.
            #
            # The value is stored as the profile gave it, not as the reader
            # produced it. The field reads the constraint through its own
            # reader again when it checks a cell, so the stored value is
            # read the same way twice, and storing what the reader produced
            # would put a Decimal in a number field's constraint - which
            # cannot be written out as JSON.
            constraints = {}
            for keyword, constraint in CONSTRAINTS_BY_TYPE.get(type, {}).items():
                value = prop.get(keyword)
                if value is None:
                    continue
                if keyword in COUNT_KEYWORDS:
                    if not _is_count(value):
                        continue
                elif _read(field, value) is None:
                    continue
                constraints[constraint] = value
            enum = prop.get("enum")
            if _carries_enum(field, enum):
                constraints["enum"] = enum
            if constraints:
                field.constraints.update(constraints)

            # Description
            description = prop.get("description")  # type: ignore
            if description:
                assert isinstance(description, str)
                field.description = description

            # Required
            if name in required:
                field.required = True

        return schema
