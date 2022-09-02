from __future__ import annotations
import attrs
from ...pipeline import Step


@attrs.define(kw_only=True)
class table_print(Step):
    """Print table"""

    type = "table-print"

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        print(table.look(vrepr=str, style="simple"))  # type: ignore
