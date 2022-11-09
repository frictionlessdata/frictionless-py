from __future__ import annotations
import attrs
from ...pipeline import Step
from ...resource import Resource
from ...dialect import Dialect


@attrs.define(kw_only=True)
class table_write(Step):
    """Write table"""

    type = "table-write"

    # State

    # TODO: rebase on resource?
    path: str
    """NOTE: add docs
    """

    # Transform

    def transform_resource(self, resource):
        dialect = None
        if "dialect" in self.custom:
            dialect = Dialect.from_descriptor(self.custom["dialect"])
        target = Resource(path=self.path, type="table", dialect=dialect)
        resource.write(target)

    # Metadata

    metadata_profile_patch = {
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
