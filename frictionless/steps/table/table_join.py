import petl
from ...step import Step
from ...resource import Resource


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_join(Step):
    """Join tables"""

    code = "table-join"

    def __init__(
        self,
        descriptor=None,
        *,
        resource=None,
        field_name=None,
        use_hash=None,
        mode=None,
    ):
        self.setinitial("resource", resource)
        self.setinitial("fieldName", field_name)
        self.setinitial("useHash", use_hash)
        self.setinitial("mode", mode)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        field_name = self.get("fieldName")
        use_hash = self.get("useHash", False)
        mode = self.get("mode", "inner")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        if mode not in ["negate"]:
            for field in source.schema.fields:
                if field.name != field_name:
                    target.schema.fields.append(field.to_copy())
        if mode == "inner":
            join = petl.hashjoin if use_hash else petl.join
            resource.data = join(view1, view2, field_name)
        elif mode == "left":
            leftjoin = petl.hashleftjoin if use_hash else petl.leftjoin
            resource.data = leftjoin(view1, view2, field_name)
        elif mode == "right":
            rightjoin = petl.hashrightjoin if use_hash else petl.rightjoin
            resource.data = rightjoin(view1, view2, field_name)
        elif mode == "outer":
            resource.data = petl.outerjoin(view1, view2, field_name)
        elif mode == "cross":
            resource.data = petl.crossjoin(view1, view2)
        elif mode == "negate":
            antijoin = petl.hashantijoin if use_hash else petl.antijoin
            resource.data = antijoin(view1, view2, field_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
            "fieldName": {"type": "string"},
            "mode": {
                "type": "string",
                "enum": ["inner", "left", "right", "outer", "cross", "negate"],
            },
            "hash": {},
        },
    }
