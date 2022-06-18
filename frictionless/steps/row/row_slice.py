from typing import Optional
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_slice(Step):
    """Slice rows"""

    code = "row-slice"

    def __init__(
        self,
        *,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
        head: Optional[int] = None,
        tail: Optional[int] = None,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.head = head
        self.tail = tail

    # Properties

    start: Optional[int]
    """TODO: add docs"""

    stop: Optional[int]
    """TODO: add docs"""

    step: Optional[int]
    """TODO: add docs"""

    head: Optional[int]
    """TODO: add docs"""

    tail: Optional[int]
    """TODO: add docs"""

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

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "code": {},
            "start": {},
            "stop": {},
            "step": {},
            "head": {},
            "tail": {},
        },
    }
