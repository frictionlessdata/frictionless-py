from __future__ import annotations
import attrs
from typing import Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class table_debug(Step):
    """Debug table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-debug"

    # State

    function: Any
    """
    Debug function to apply to the table row.
    """

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()

        # Data
        def data():
            with current:
                for row in current.row_stream:  # type: ignore
                    self.function(row)  # type: ignore
                    yield row

        # Meta
        resource.data = data

    # Metadata

    metadata_profile_patch = {
        "required": ["function"],
        "properties": {
            "function": {},
        },
    }
