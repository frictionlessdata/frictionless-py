from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, List, Any
from petl.compat import next, text_type
from ...pipeline import Step
from ... import fields

if TYPE_CHECKING:
    from ...resource import Resource

DEFAULT_SEPARATOR = "-"


@attrs.define(kw_only=True)
class field_merge(Step):
    """Merge fields.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "field-merge"

    # State

    name: str
    """
    Name of the new field that will be created after merge.
    """

    from_names: List[str]
    """
    List of field names to merge.
    """

    separator: str = DEFAULT_SEPARATOR
    """
    Separator to use while merging values of the two fields.
    """

    preserve: bool = False
    """
    It indicates if the fields are preserved or not after merging. If True,
    fields will not be removed and vice versa.
    """

    # Transform

    def transform_resource(self, resource: Resource) -> None:
        table = resource.to_petl()
        field = fields.StringField(name=self.name)
        resource.schema.add_field(field)
        if not self.preserve:
            for name in self.from_names:
                resource.schema.remove_field(name)
        resource.data = merge(
            table,
            self.name,
            self.from_names,
            self.separator,
            self.preserve,
        )

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "fromNames"],
        "properties": {
            "name": {"type": "string"},
            "fromNames": {"type": "array"},
            "fieldType": {"type": "string"},
            "separator": {"type": "string"},
            "preserve": {"type": "boolean"},
        },
    }


# Internal


def merge(
    source: Any,
    name: str,
    from_names: list,
    sep: str = "-",
    preserve: bool = True,
):
    it = iter(source)

    hdr = next(it)
    field_indexes = list()
    flds = list(map(text_type, hdr))

    # determine output fields
    outhdr = list(flds)
    for field in from_names:
        field_index = flds.index(field)
        if not preserve:
            outhdr.remove(field)
        field_indexes.append(field_index)
    outhdr.extend([name])
    yield tuple(outhdr)

    # construct the output data
    for row in it:
        value = [v for i, v in enumerate(row) if i in field_indexes]
        if preserve:
            out_row = list(row)
        else:
            out_row = [v for i, v in enumerate(row) if i not in field_indexes]
        out_row.extend([sep.join(value)])
        yield tuple(out_row)
