from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_debug(Step):
    """Debug table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-debug"

    function: Any
    """
    Debug function to apply to the table row.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        current = resource.to_copy()

        # Data
        def data():  # type: ignore
            with current:
                for row in current.row_stream:  # type: ignore
                    self.function(row)  # type: ignore
                    yield row

        # Meta
        resource.data = data

    # Metadata

    metadata_profile_patch = {  # type: ignore
        "required": ["function"],
        "properties": {
            "function": {},
        },
    }
