import simpleeval
from ...step import Step
from ...field import Field
from ... import helpers


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_add(Step):
    """Add field"""

    code = "field-add"

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        value=None,
        formula=None,
        function=None,
        position=None,
        incremental=False,
        **options,
    ):
        self.setinitial("name", name)
        self.setinitial("value", value)
        self.setinitial("formula", formula)
        self.setinitial("function", function)
        self.setinitial("position", position if not incremental else 1)
        self.setinitial("incremental", incremental)
        for key, value in helpers.create_descriptor(**options).items():
            self.setinitial(key, value)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        descriptor = self.to_dict()
        descriptor.pop("code", None)  # type: ignore
        name = descriptor.pop("name", None)  # type: ignore
        value = descriptor.pop("value", None)  # type: ignore
        formula = descriptor.pop("formula", None)  # type: ignore
        function = descriptor.pop("function", None)  # type: ignore
        position = descriptor.pop("position", None)  # type: ignore
        incremental = descriptor.pop("incremental", None)  # type: ignore
        field = Field(descriptor, name=name)
        index = position - 1 if position else None
        if index is None:
            resource.schema.add_field(field)
        else:
            resource.schema.fields.insert(index, field)
        if incremental:
            resource.data = table.addrownumbers(field=name)  # type: ignore
        else:
            if formula:
                function = lambda row: simpleeval.simple_eval(formula, names=row)
            value = value or function
            resource.data = table.addfield(name, value=value, index=index)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "value": {},
            "position": {},
            "incremental": {},
        },
    }
