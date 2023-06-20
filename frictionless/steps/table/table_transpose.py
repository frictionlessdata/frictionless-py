from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

from ...pipeline import Step
from ...schema import Schema

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
