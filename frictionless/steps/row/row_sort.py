from typing import List
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_sort(Step):
    """Sort rows"""

    code = "row-sort"

    def __init__(
        self,
        *,
        field_names: List[str],
        reverse: bool = False,
    ):
        self.field_names = field_names
        self.reverse = reverse

    # Properties

    field_names: List[str]
    """TODO: add docs"""

    reverse: bool
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.sort(self.field_names, reverse=self.reverse)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldNames"],
        "properties": {
            "code": {},
            "fieldNames": {"type": "array"},
            "reverse": {},
        },
    }
