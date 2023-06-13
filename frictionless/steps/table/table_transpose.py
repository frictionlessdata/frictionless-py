from __future__ import annotations
import attrs
from typing import TYPE_CHECKING
from ...schema import Schema
from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_transpose(Step):
    """Transpose table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-transpose"

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        resource.schema = Schema()
        resource.data = table.transpose()  # type: ignore
        resource.infer()
