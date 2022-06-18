from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_set(Step):
    """Set cell"""

    code = "cell-set"

    def __init__(
        self,
        *,
        value: str,
        field_name: str,
    ):
        self.value = value
        self.field_name = field_name

    # Properties

    value: str
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "code": {},
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
