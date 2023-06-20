from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_print(Step):
    """Print table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-print"

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        print(table.look(vrepr=str, style="simple"))  # type: ignore
