from ...step import Step
from ...field import Field
from typing import List, Iterator
from petl.compat import next, text_type


def merge(
    source: any, name: str, from_names: list, sep: str = "-", preserve: bool = True
) -> Iterator:
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


class field_merge(Step):
    """Merge fields

    API      | Usage
    -------- | --------
    Public   | `from frictionless import steps`
    Implicit | `validate(checks=([{"code": "field-merge", **descriptor}])`

    This step can be added using the `steps` parameter
    for the `transform` function.

    Parameters:
       descriptor (dict): step's descriptor
       name (str): name of new field
       from_names (str): field names to merge
       field_type? (str): type of new field
       separator? (str): delimeter to use
       preserve? (bool): preserve source fields

    """

    code = "field-merge"

    def __init__(
        self,
        descriptor: any = None,
        *,
        name: str = None,
        from_names: List[str] = None,
        field_type: str = None,
        separator: str = "-",
        preserve: bool = False
    ):
        self.setinitial("name", name)
        self.setinitial("fromNames", from_names)
        self.setinitial("fieldType", field_type)
        self.setinitial("separator", separator)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource: any) -> None:
        table = resource.to_petl()
        name = self.get("name")
        from_names = self.get("fromNames")
        field_type = self.get("fieldType", "string")
        separator = self.get("separator")
        preserve = self.get("preserve")
        resource.schema.add_field(Field(name=name, type=field_type))
        if not preserve:
            for name in from_names:
                resource.schema.remove_field(name)
        resource.data = merge(table, name, from_names, separator, preserve)

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["name", "fromNames"],
        "properties": {
            "name": {"type": "string"},
            "fromNames": {"type": "array"},
            "fieldType": {"type": "string"},
            "separator": {"type": "string"},
            "preserve": {"type": "boolean"},
        },
    }
