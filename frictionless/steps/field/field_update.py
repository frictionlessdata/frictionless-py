import simpleeval
from ...step import Step
from ... import helpers


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_update(Step):
    """Update field"""

    code = "field-update"

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        value=None,
        formula=None,
        function=None,
        new_name=None,
        **options,
    ):
        self.setinitial("name", name)
        self.setinitial("value", value)
        self.setinitial("formula", formula)
        self.setinitial("function", function)
        self.setinitial("newName", new_name)
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
        new_name = descriptor.pop("newName", None)  # type: ignore
        if new_name:
            descriptor["name"] = new_name  # type: ignore
        field = resource.schema.get_field(name)
        field.update(descriptor)
        if formula:
            function = lambda val, row: simpleeval.simple_eval(formula, names=row)
        if function:
            resource.data = table.convert(name, function)  # type: ignore
        elif new_name:
            resource.data = table.rename({name: new_name})  # type: ignore
        elif "value" in self:
            resource.data = table.update(name, value)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "newName": {"type": "string"},
        },
    }
