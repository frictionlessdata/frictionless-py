from __future__ import annotations

from typing import Union

import attrs

from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_attach(Step):
    """Attach table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-attach"

    resource: Union[Resource, str]
    """
    Data Resource to attach to the existing table.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        source = self.resource
        target = resource
        if isinstance(source, str):
            assert target.package
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()  # type: ignore
        view2 = source.to_petl()  # type: ignore
        for field in source.schema.fields:
            target.schema.fields.append(field.to_copy())
        resource.data = platform.petl.annex(view1, view2)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {"type": ["object", "string"]},
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "resource":
            return Resource
