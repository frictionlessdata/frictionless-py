from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class row_slice(Step):
    """Slice rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-slice"

    start: Optional[int] = None
    """
    Starting point from where to read the rows. If None,
    defaults to the beginning.
    """

    stop: Optional[int] = None
    """
    Stopping point for reading row. If None, defaults to
    the end.
    """

    step: Optional[int] = None
    """
    It is the step size to read next row. If None, it defaults
    to 1.
    """

    head: Optional[int] = None
    """
    Number of rows to read from head.
    """

    tail: Optional[int] = None
    """
    Number of rows to read from the bottom.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        if self.head:
            resource.data = table.head(self.head)  # type: ignore
        elif self.tail:
            resource.data = table.tail(self.tail)  # type: ignore
        else:
            resource.data = table.rowslice(self.start, self.stop, self.step)  # type: ignore

    # Metadata

    metadata_profile_patch = {  # type: ignore
        "properties": {
            "start": {},
            "stop": {},
            "step": {},
            "head": {},
            "tail": {},
        },
    }
