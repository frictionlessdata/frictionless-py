import petl
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_ungroup(Step):
    """Ungroup rows"""

    code = "row-ungroup"

    def __init__(
        self,
        descriptor=None,
        *,
        selection=None,
        group_name=None,
        value_name=None,
    ):
        self.setinitial("selection", selection)
        self.setinitial("groupName", group_name)
        self.setinitial("valueName", value_name)
        super().__init__(descriptor)

    def transform_resource(self, resource):
        table = resource.to_petl()
        selection = self.get("selection")
        group_name = self.get("groupName")
        value_name = self.get("valueName")
        function = getattr(petl, f"groupselect{selection}")
        if selection in ["first", "last"]:
            resource.data = function(table, group_name)
        else:
            resource.data = function(table, group_name, value_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "selection"],
        "properties": {
            "selection": {
                "type": "string",
                "enum": ["first", "last", "min", "max"],
            },
            "groupName": {"type": "string"},
            "valueName": {"type": "string"},
        },
    }
