from __future__ import annotations
import attrs
from ...pipeline import Step
from ...dialect import Dialect
from ... import resources


@attrs.define(kw_only=True)
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

    def transform_resource(self, resource):
        target = resources.TableResource(path=self.path)
        if "dialect" in self.custom:
            dialect = Dialect.from_descriptor(self.custom["dialect"])
            target.dialect = dialect
        resource.write(target)

    # Metadata

    metadata_profile_patch = {
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
