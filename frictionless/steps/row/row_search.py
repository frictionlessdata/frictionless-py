import petl
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_search(Step):
    """Search rows"""

    code = "row-search"

    def __init__(self, descriptor=None, *, regex=None, field_name=None, negate=False):
        self.setinitial("regex", regex)
        self.setinitial("fieldName", field_name)
        self.setinitial("negate", negate)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        regex = self.get("regex")
        field_name = self.get("fieldName")
        negate = self.get("negate")
        search = petl.searchcomplement if negate else petl.search
        if field_name:
            resource.data = search(table, field_name, regex)
        else:
            resource.data = search(table, regex)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["regex"],
        "properties": {
            "regex": {},
            "fieldName": {"type": "string"},
            "negate": {},
        },
    }
