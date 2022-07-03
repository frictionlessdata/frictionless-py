from dataclasses import dataclass
from .header import HeaderError


@dataclass
class LabelError(HeaderError):
    """Label error representation"""

    code = "label-error"
    name = "Label Error"
    tags = ["#table", "#header", "#label"]
    template = "Label Error"
    description = "Label Error"

    # State

    label: str
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

    field_number: int
    """TODO: add docs"""

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["note"],
        "properties": {
            "code": {},
            "name": {},
            "tags": {},
            "description": {},
            "message": {},
            "note": {},
            "labels": {},
            "rowNumbers": {},
            "label": {},
            "fieldName": {},
            "fieldNumber": {},
        },
    }


class ExtraLabelError(LabelError):
    code = "extra-label"
    name = "Extra Label"
    template = 'There is an extra label "{label}" in header at position "{fieldNumber}"'
    description = "The header of the data source contains label that does not exist in the provided schema."


class MissingLabelError(LabelError):
    code = "missing-label"
    name = "Missing Label"
    template = 'There is a missing label in the header\'s field "{fieldName}" at position "{fieldNumber}"'
    description = "Based on the schema there should be a label that is missing in the data's header."


class BlankLabelError(LabelError):
    code = "blank-label"
    name = "Blank Label"
    template = 'Label in the header in field at position "{fieldNumber}" is blank'
    description = "A label in the header row is missing a value. Label should be provided and not be blank."


class DuplicateLabelError(LabelError):
    code = "duplicate-label"
    name = "Duplicate Label"
    template = 'Label "{label}" in the header at position "{fieldNumber}" is duplicated to a label: {note}'
    description = "Two columns in the header row have the same value. Column names should be unique."


class IncorrectLabelError(LabelError):
    code = "incorrect-label"
    name = "Incorrect Label"
    template = 'Label "{label}" in field {fieldName} at position "{fieldNumber}" does not match the field name in the schema'
    description = "One of the data source header does not match the field name defined in the schema."
