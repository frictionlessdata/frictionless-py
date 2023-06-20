from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

from ...dialect import Dialect
from ...pipeline import Step
from ...resources import TableResource

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_write(Step):
    """Write table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-write"

    # TODO: rebase on resource?
    path: str
    """
    Path of the file to write the table content.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        assert isinstance(resource, TableResource)
        target = TableResource(path=self.path)
        if "dialect" in self.custom:
            dialect = Dialect.from_descriptor(self.custom["dialect"])
            target.dialect = dialect
        resource.write_table(target)

    # Metadata

    metadata_profile_patch = {
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
