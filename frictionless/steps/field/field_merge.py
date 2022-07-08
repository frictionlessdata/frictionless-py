# type: ignore
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Any, Optional
from petl.compat import next, text_type
from ...schema import Field
from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@dataclass
class field_merge(Step):
    """Merge fields

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    code = "field-merge"

    # Properties

    name: str
    """TODO: add docs"""

    from_names: List[str]
    """TODO: add docs"""

    field_type: Optional[str] = None
    """TODO: add docs"""

    separator: Optional[str] = None
    """TODO: add docs"""

    preserve: bool = False
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource: Resource) -> None:
        table = resource.to_petl()
        resource.schema.add_field(Field(name=self.name, type=self.field_type))
        if not self.preserve:
            for name in self.from_names:
                resource.schema.remove_field(name)
        resource.data = merge(  # type: ignore
            table, self.name, self.from_names, self.separator, self.preserve  # type: ignore
        )

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["name", "fromNames"],
        "properties": {
            "code": {},
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
