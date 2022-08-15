from __future__ import annotations
import attrs
from typing import Union
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True)
class table_diff(Step):
    """Diff tables"""

    type = "table-diff"

    # State

    resource: Union[Resource, str]
    """NOTE: add docs
    """

    ignore_order: bool = False
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
            platform.petl.recordcomplement
            if self.ignore_order
            else platform.petl.complement
        )
        # NOTE: we might raise an error for ignore/hash
        if self.use_hash and not self.ignore_order:
            function = platform.petl.hashcomplement
        resource.data = function(view1, view2)

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {"type": ["object", "string"]},
            "ignoreOrder": {"type": "boolean"},
            "useHash": {"type": "boolean"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "resource":
            return Resource
