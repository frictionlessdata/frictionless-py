from __future__ import annotations

from typing import List, Optional, Union

import attrs

from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_merge(Step):
    """Merge tables.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-merge"

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

    def transform_resource(self, resource: Resource):
        target = resource
        source = self.resource
        if isinstance(source, str):
            assert target.package
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()  # type: ignore
        view2 = source.to_petl()  # type: ignore

        # Ignore fields
        if self.ignore_fields:
            for field in source.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)
            resource.data = platform.petl.stack(view1, view2)  # type: ignore

        # Default
        else:
            for field in source.schema.fields:
                if not target.schema.has_field(field.name):  # type: ignore
                    target.schema.add_field(field.to_copy())
            if self.field_names:
                for field in list(target.schema.fields):
                    if field.name not in self.field_names:
                        target.schema.remove_field(field.name)  # type: ignore
            field_names = self.field_names or None
            if self.sort_by_field:
                key = self.sort_by_field
                resource.data = platform.petl.mergesort(  # type: ignore
                    view1, view2, key=key, header=field_names  # type: ignore
                )
            else:
                resource.data = platform.petl.cat(view1, view2, header=field_names)  # type: ignore

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
    def metadata_select_property_class(cls, name: str):
        if name == "resource":
            return Resource
