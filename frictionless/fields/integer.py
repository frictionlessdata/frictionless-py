from ..schema.field import Field


class IntegerField(Field):
    ### TEMP Only required for Metadata compatibility
    ### This is required because "metadata_import" makes a distinction based
    ### on the "type" property (`is_typed_class`)
    type = "integer"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]
