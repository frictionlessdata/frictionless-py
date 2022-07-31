from __future__ import annotations
import attrs
from typing import Any
from ...pipeline import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


@attrs.define(kw_only=True)
class table_debug(Step):
    """Debug table"""

    type = "table-debug"

    # State

    function: Any
    """NOTE: add docs"""

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
