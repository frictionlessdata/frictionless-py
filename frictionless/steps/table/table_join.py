from __future__ import annotations
import attrs
from typing import Union, Optional
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


DEFAULT_MODE = "inner"


@attrs.define(kw_only=True)
class table_join(Step):
    """Join tables.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-join"

    # State

    resource: Union[Resource, str]
    """
    Resource with which to apply join.
    """

    field_name: Optional[str] = None
    """
    Field name with which the join will be performed comparing it's value between two tables. 
    If not provided natural join is tried. For more information, please see the following document:
    https://petl.readthedocs.io/en/stable/_modules/petl/transform/joins.html
    """

    use_hash: bool = False
    """
    Specify whether to use hash or not. If True, an alternative implementation of join will be used.
    """

    mode: str = DEFAULT_MODE
    """
    Specifies which mode to use. The available modes are: "inner", "left", "right", "outer", "cross" and 
    "negate". The default mode is "inner".
    """

    # Transform

    def transform_resource(self, resource):
        target = resource
        source = self.resource
        if isinstance(source, str):
            assert target.package
            source = target.package.get_resource(source)
        source.infer()  # type: ignore
        view1 = target.to_petl()
        view2 = source.to_petl()  # type: ignore
        if self.mode not in ["negate"]:
            for field in source.schema.fields:  # type: ignore
                if field.name != self.field_name:
                    target.schema.fields.append(field.to_copy())
        if self.mode == "inner":
            join = platform.petl.hashjoin if self.use_hash else platform.petl.join
            resource.data = join(view1, view2, self.field_name)  # type: ignore
        elif self.mode == "left":
            leftjoin = (
                platform.petl.hashleftjoin if self.use_hash else platform.petl.leftjoin
            )
            resource.data = leftjoin(view1, view2, self.field_name)  # type: ignore
        elif self.mode == "right":
            rightjoin = (
                platform.petl.hashrightjoin if self.use_hash else platform.petl.rightjoin
            )
            resource.data = rightjoin(view1, view2, self.field_name)  # type: ignore
        elif self.mode == "outer":
            resource.data = platform.petl.outerjoin(view1, view2, self.field_name)  # type: ignore
        elif self.mode == "cross":
            resource.data = platform.petl.crossjoin(view1, view2)  # type: ignore
        elif self.mode == "negate":
            antijoin = (
                platform.petl.hashantijoin if self.use_hash else platform.petl.antijoin
            )
            resource.data = antijoin(view1, view2, self.field_name)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {"type": ["object", "string"]},
            "fieldName": {"type": "string"},
            "mode": {
                "type": "string",
                "enum": ["inner", "left", "right", "outer", "cross", "negate"],
            },
            "hash": {},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "resource":
            return Resource
