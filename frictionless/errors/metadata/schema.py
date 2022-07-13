from __future__ import annotations
from .metadata import MetadataError


class SchemaError(MetadataError):
    type = "schema-error"
    title = "Schema Error"
    description = "Provided schema is not valid."
    template = "Schema is not valid: {note}"


class FieldError(SchemaError):
    type = "field-error"
    title = "Field Error"
    description = "Provided field is not valid."
    template = "Field is not valid: {note}"
