from __future__ import annotations

from typing import Union

import attrs

from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_intersect(Step):
    """Intersect tables.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-intersect"

    resource: Union[Resource, str]
    """
    Resource with which to apply intersection.
    """

    use_hash: bool = False
    """
    Specifies whether to use hash or not. If yes, an
    alternative implementation will be used. For more
    information please see the link below:
    https://petl.readthedocs.io/en/stable/transform.html#petl.transform.setops.hashintersection
    """

    # Transform

    def transform_resource(self, resource: Resource):
        target = resource
        source = self.resource
        if isinstance(source, str):
            assert target.package
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()  # type: ignore
        view2 = source.to_petl()  # type: ignore
        function = (  # type: ignore
            platform.petl.hashintersection  # type: ignore
            if self.use_hash
            else platform.petl.intersection  # type: ignore
        )
        resource.data = function(view1, view2)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {"type": ["object", "string"]},
            "useHash": {"type": "boolean"},
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "resource":
            return Resource
