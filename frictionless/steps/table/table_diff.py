from __future__ import annotations

from typing import Union

import attrs

from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_diff(Step):
    """Diff tables.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-diff"

    resource: Union[Resource, str]
    """
    Resource with which to compare.
    """

    ignore_order: bool = False
    """
    Specifies whether to ignore the order of the rows.
    """

    use_hash: bool = False
    """
    Specifies whether to use hash or not. If yes, alternative implementation will
    be used where the complement is executed by constructing an in-memory set for
    all rows found in the right hand table. For more information
    please see the link below:
    https://petl.readthedocs.io/en/stable/transform.html#petl.transform.setops.hashcomplement
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
            platform.petl.recordcomplement  # type: ignore
            if self.ignore_order
            else platform.petl.complement  # type: ignore
        )
        # NOTE: we might raise an error for ignore/hash
        if self.use_hash and not self.ignore_order:
            function = platform.petl.hashcomplement  # type: ignore
        resource.data = function(view1, view2)  # type: ignore

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
    def metadata_select_property_class(cls, name: str):
        if name == "resource":
            return Resource
