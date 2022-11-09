from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_slice(Step):
    """Slice rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-slice"

    # State

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

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.head:
            resource.data = table.head(self.head)  # type: ignore
        elif self.tail:
            resource.data = table.tail(self.tail)  # type: ignore
        else:
            resource.data = table.rowslice(self.start, self.stop, self.step)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "start": {},
            "stop": {},
            "step": {},
            "head": {},
            "tail": {},
        },
    }
