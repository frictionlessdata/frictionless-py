from __future__ import annotations
import attrs
from typing import Optional
from ...platform import platform
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_search(Step):
    """Search rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-search"

    # State

    regex: str
    """
    Regex pattern to search for rows. If field_name is set it 
    will only be applied to the specified field. For example, regex=r"^e.*".
    """

    field_name: Optional[str] = None
    """
    Field name in which to search for.
    """

    negate: bool = False
    """
    Whether to revert the result. If True, all the rows that does 
    not match the pattern will be returned.
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        search = platform.petl.searchcomplement if self.negate else platform.petl.search
        if self.field_name:
            resource.data = search(table, self.field_name, self.regex)  # type: ignore
        else:
            resource.data = search(table, self.regex)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["regex"],
        "properties": {
            "regex": {},
            "fieldName": {"type": "string"},
            "negate": {},
        },
    }
