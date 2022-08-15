from __future__ import annotations
import attrs
from typing import Union
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True)
class table_intersect(Step):
    """Intersect tables"""

    type = "table-intersect"

    # State

    resource: Union[Resource, str]
    """NOTE: add docs
    """

    use_hash: bool = False
    """NOTE: add docs
    """

    # Transform

    def transform_resource(self, resource):
        target = resource
        source = self.resource
        if isinstance(source, str):
            assert target.package
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        function = (
            platform.petl.hashintersection
            if self.use_hash
            else platform.petl.intersection
        )
        resource.data = function(view1, view2)

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {"type": ["object", "string"]},
            "useHash": {"type": "boolean"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "resource":
            return Resource
