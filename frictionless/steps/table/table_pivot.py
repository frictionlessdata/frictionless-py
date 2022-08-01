# type: ignore
from __future__ import annotations
from ...pipeline import Step


# TODO: migrate
class table_pivot(Step):
    """Pivot table"""

    type = "table-pivot"

    def __init__(self, descriptor=None, **options):
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        options = self.get("options")
        resource.pop("schema", None)
        resource.data = table.pivot(**options)  # type: ignore
        resource.infer()
