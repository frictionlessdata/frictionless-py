from __future__ import annotations
import attrs
from ...pipeline import Step


@attrs.define(kw_only=True)
class table_normalize(Step):
    """Normalize table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-normalize"

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()

        # Data
        def data():
            with current:
                yield current.header.to_list()  # type: ignore
                for row in current.row_stream:  # type: ignore
                    yield row.to_list()

        # Meta
        resource.data = data
