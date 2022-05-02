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
        descriptor.pop("code", None)
        name = descriptor.pop("name", None)
        value = descriptor.pop("value", None)
        formula = descriptor.pop("formula", None)
        function = descriptor.pop("function", None)
        new_name = descriptor.pop("newName", None)
        if new_name:
            descriptor["name"] = new_name
        field = resource.schema.get_field(name)
        field.update(descriptor)
        if formula:
            function = lambda val, row: simpleeval.simple_eval(formula, names=row)
        if function:
            resource.data = table.convert(name, function)
        elif new_name:
            resource.data = table.rename({name: new_name})
        elif "value" in self:
            resource.data = table.update(name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "newName": {"type": "string"},
        },
    }
