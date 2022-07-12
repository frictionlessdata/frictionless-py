from .metadata import MetadataError


class SchemaError(MetadataError):
    name = "Schema Error"
    type = "schema-error"
    template = "Schema is not valid: {note}"
    description = "Provided schema is not valid."


class FieldError(SchemaError):
    name = "Field Error"
    type = "field-error"
    template = "Field is not valid: {note}"
    description = "Provided field is not valid."
