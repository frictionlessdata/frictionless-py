from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_slice(Step):
    """Slice rows"""

    code = "row-slice"

    def __init__(
        self,
        descriptor=None,
        *,
        start=None,
        stop=None,
        step=None,
        head=None,
        tail=None,
    ):
        self.setinitial("start", start)
        self.setinitial("stop", stop)
        self.setinitial("step", step)
        self.setinitial("head", head)
        self.setinitial("tail", tail)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        start = self.get("start")
        stop = self.get("stop")
        step = self.get("step")
        head = self.get("head")
        tail = self.get("tail")
        if head:
            resource.data = table.head(head)
        elif tail:
            resource.data = table.tail(tail)
        else:
            resource.data = table.rowslice(start, stop, step)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "start": {},
            "stop": {},
            "step": {},
            "head": {},
            "tail": {},
        },
    }
