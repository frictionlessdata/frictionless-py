from __future__ import annotations
import attrs
from .header import HeaderError


@attrs.define(kw_only=True)
class LabelError(HeaderError):
    """Label error representation.

    A base class for all the errors related to the labels of the columns/fields.

    """

    type = "label-error"
    title = "Label Error"
    description = "Label Error"
    template = "Label Error"
    tags = ["#table", "#header", "#label"]

    # State

    label: str
    """
    Label of the field that has an error.
    """

    field_name: str
    """
    Name of the field that has an error.
    """

    field_number: int
    """
    Index of the field that has an error.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "label": {"type": "string"},
            "fieldName": {"type": "string"},
            "fieldNumber": {"type": "integer"},
        },
    }


class ExtraLabelError(LabelError):
    type = "extra-label"
    title = "Extra Label"
    description = "The header of the data source contains label that does not exist in the provided schema."
    template = 'There is an extra label "{label}" in header at position "{fieldNumber}"'


class MissingLabelError(LabelError):
    type = "missing-label"
    title = "Missing Label"
    description = "Based on the schema there should be a label that is missing in the data's header."
    template = 'There is a missing label in the header\'s field "{fieldName}" at position "{fieldNumber}"'


class BlankLabelError(LabelError):
    type = "blank-label"
    title = "Blank Label"
    description = "A label in the header row is missing a value. Label should be provided and not be blank."
    template = 'Label in the header in field at position "{fieldNumber}" is blank'


class DuplicateLabelError(LabelError):
    type = "duplicate-label"
    title = "Duplicate Label"
    description = "Two columns in the header row have the same value. Column names should be unique."
    template = 'Label "{label}" in the header at position "{fieldNumber}" is duplicated to a label: {note}'


class IncorrectLabelError(LabelError):
    type = "incorrect-label"
    title = "Incorrect Label"
    description = "One of the data source header does not match the field name defined in the schema."
    template = 'Label "{label}" in field {fieldName} at position "{fieldNumber}" does not match the field name in the schema'
