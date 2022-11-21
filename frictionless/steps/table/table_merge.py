from __future__ import annotations
import attrs
from typing import Union, List, Optional
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True)
class table_merge(Step):
    """Merge tables.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-merge"

    # State

    resource: Union[Resource, str]
    """
    Resource to merge with.
    """

    field_names: List[str] = attrs.field(factory=list)
    """
    Specifies fixed headers for output table.
    """

    sort_by_field: Optional[str] = None
    """
    Field name by which to sort the record after merging.
    """

    ignore_fields: bool = False
    """
    If ignore_fields is set to True, it will merge two resource 
    without matching headers.
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
