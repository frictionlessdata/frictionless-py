from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_normalize(Step):
    """Normalize table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-normalize"

    # Transform

    def transform_resource(self, resource: Resource):
        resource_copy = resource.to_copy()

        # Data
        def data():  # type: ignore
            # Yield from a copy to avoid side effects (see #1622)
            with resource_copy.to_copy() as current:
                yield current.header.to_list()  # type: ignore
                for row in current.row_stream:  # type: ignore
                    yield row.to_list()  # type: ignore

        # Meta
        resource.data = data
