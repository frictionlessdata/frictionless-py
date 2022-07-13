# type: ignore
from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, Any, List, Iterator, Optional
from petl.compat import next, text_type
from ...schema import Field
from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True)
class field_pack(Step):
    """Pack fields"""

    type = "field-pack"

    # State

    name: str
    """TODO: add docs"""

    from_names: List[str]
    """TODO: add docs"""

    field_type: Optional[str] = None
    """TODO: add docs"""

    preserve: bool = False
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource: Resource) -> None:
        table = resource.to_petl()
        resource.schema.add_field(Field(name=self.name, type=self.field_type))
        if not self.preserve:
            for name in self.from_names:  # type: ignore
                resource.schema.remove_field(name)
        if self.field_type == "object":
            resource.data = iterpackdict(  # type: ignore
                table, self.name, self.from_names, self.preserve  # type: ignore
            )
        else:
            resource.data = iterpack(table, self.name, self.from_names, self.preserve)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "fromNames"],
        "properties": {
            "name": {"type": "string"},
            "fromNames": {"type": "array"},
            "fieldType": {"type": "string"},
            "preserve": {"type": "boolean"},
        },
    }


# Internal


def iterpack(
    source: Any,
    name: str,
    from_names: list,
    preserve: bool = False,
) -> Iterator:
    """Combines multiple columns as array
    Code partially referenced from https://github.com/petl-developers/petl/blob/master/petl/transform/unpacks.py#L64
    """
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
        out_row.extend([value])
        yield tuple(out_row)


def iterpackdict(
    source: Any,
    name: str,
    from_names: list,
    preserve: bool = False,
) -> Iterator:
    """Combines multiple columns as JSON Object"""
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
        value = dict(
            (from_names[i - 1], v) for i, v in enumerate(row) if i in field_indexes
        )
        if preserve:
            out_row = list(row)
        else:
            out_row = [v for i, v in enumerate(row) if i not in field_indexes]
        out_row.extend([value])
        yield tuple(out_row)
