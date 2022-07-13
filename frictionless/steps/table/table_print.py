from __future__ import annotations
import attrs
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
class table_print(Step):
    """Print table"""

    type = "table-print"

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        print(table.look(vrepr=str, style="simple"))  # type: ignore
