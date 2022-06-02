from __future__ import annotations
from ...step import Step
from ...field import Field
from typing import TYPE_CHECKING, Any, List, Iterator, Optional
from petl.compat import next, text_type

if TYPE_CHECKING:
    from ...resource import Resource


class field_pack(Step):
    """Pack fields

    API      | Usage
    -------- | --------
    Public   | `from frictionless import steps`
    Implicit | `validate(checks=([{"code": "field-pack", **descriptor}])`

    This step can be added using the `steps` parameter
    for the `transform` function.

    Parameters:
       descriptor (dict): step's descriptor
       name (str): name of new field
       from_names (str): field names to pack
       field_type? (str): type of new field
       preserve? (bool): preserve source fields

    """

    code = "field-pack"

    def __init__(
        self,
        descriptor=None,
        *,
        name: Optional[str] = None,
        from_names: Optional[List[str]] = None,
        field_type: Optional[str] = None,
        preserve: bool = False,
    ):
        self.setinitial("name", name)
        self.setinitial("fromNames", from_names)
        self.setinitial("fieldType", field_type)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource: Resource) -> None:
        table = resource.to_petl()
        name = self.get("name")
        from_names = self.get("fromNames")
        field_type = self.get("fieldType", "array")
        preserve = self.get("preserve")
        resource.schema.add_field(Field(name=name, type=field_type))
        if not preserve:
            for name in from_names:  # type: ignore
                resource.schema.remove_field(name)
        if field_type == "object":
            resource.data = iterpackdict(  # type: ignore
                table, "detail", ["name", "population"], preserve  # type: ignore
            )
        else:
            resource.data = iterpack(table, "detail", ["name", "population"], preserve)  # type: ignore

    # Metadata

    metadata_profile = {
        "type": "object",
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
