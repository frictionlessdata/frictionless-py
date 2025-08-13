from ..schema.field import Field


class BooleanField(Field):
    ### TEMP Only required for Metadata compatibility
    ### This is required because "metadata_import" makes a distinction based
    ### on the "type" property (`is_typed_class`)
    type = "boolean"
