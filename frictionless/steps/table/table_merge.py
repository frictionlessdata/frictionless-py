from __future__ import annotations
import attrs
from typing import Union, List, Optional
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True)
class table_merge(Step):
    """Merge tables"""

    type = "table-merge"

    # State

    resource: Union[Resource, str]
    """NOTE: add docs
    """

    field_names: List[str] = attrs.field(factory=list)
    """NOTE: add docs
    """

    sort_by_field: Optional[str] = None
    """NOTE: add docs
    """

    ignore_fields: bool = False
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

        # Ignore fields
        if self.ignore_fields:
            for field in source.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)
            resource.data = platform.petl.stack(view1, view2)

        # Default
        else:
            for field in source.schema.fields:
                if not target.schema.has_field(field.name):  # type: ignore
                    target.schema.add_field(field.to_copy())
            if self.field_names:
                for field in list(target.schema.fields):
                    if field.name not in self.field_names:
                        target.schema.remove_field(field.name)  # type: ignore
            if self.sort_by_field:
                key = self.sort_by_field
                resource.data = platform.petl.mergesort(
                    view1, view2, key=key, header=self.field_names
                )
            else:
                resource.data = platform.petl.cat(view1, view2, header=self.field_names)

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {"type": ["object", "string"]},
            "fieldNames": {"type": "array"},
            "sortByField": {"type": "string"},
            "ignoreFields": {"type": "boolean"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "resource":
            return Resource
