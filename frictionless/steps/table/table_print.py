from __future__ import annotations
import attrs
from typing import TYPE_CHECKING
from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True)
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
