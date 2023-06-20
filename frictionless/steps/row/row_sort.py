from __future__ import annotations

from typing import TYPE_CHECKING, List

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class row_sort(Step):
    """Sort rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-sort"

    field_names: List[str]
    """
    List of field names by which the rows will be
    sorted. If fields more than 1, sort applies from
    left to right.
    """

    reverse: bool = False
    """
    The sort will be reversed if it is set to True.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        resource.data = table.sort(self.field_names, reverse=self.reverse)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldNames"],
        "properties": {
            "fieldNames": {"type": "array"},
            "reverse": {},
        },
    }
