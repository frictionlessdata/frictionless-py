# type: ignore
from __future__ import annotations
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


# TODO: migrate
class table_diff(Step):
    """Diff tables"""

    type = "table-diff"

    def __init__(
        self,
        descriptor=None,
        *,
        resource=None,
        ignore_order=False,
        use_hash=False,
    ):
        self.setinitial("resource", resource)
        self.setinitial("ignoreOrder", ignore_order)
        self.setinitial("useHash", use_hash)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        ignore_order = self.get("ignoreOrder")
        use_hash = self.get("useHash")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()  # type: ignore
        view1 = target.to_petl()
        view2 = source.to_petl()  # type: ignore
        function = (
            platform.petl.recordcomplement if ignore_order else platform.petl.complement
        )
        # NOTE: we might raise an error for ignore/hash
        if use_hash and not ignore_order:
            function = platform.petl.hashcomplement
        resource.data = function(view1, view2)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {},
            "ignoreOrder": {},
            "useHash": {},
        },
    }
