from .metadata import MetadataError


class SchemaError(MetadataError):
    code = "schema-error"
    name = "Schema Error"
    template = "Schema is not valid: {note}"
    description = "Provided schema is not valid."


class FieldError(SchemaError):
    code = "field-error"
    name = "Field Error"
    template = "Field is not valid: {note}"
    description = "Provided field is not valid."
