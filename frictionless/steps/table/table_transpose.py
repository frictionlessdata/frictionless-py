from __future__ import annotations
import attrs
from ...pipeline import Step


@attrs.define(kw_only=True)
class table_transpose(Step):
    """Transpose table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-transpose"

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.schema = None
        resource.data = table.transpose()  # type: ignore
        resource.infer()
