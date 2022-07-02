import simpleeval
from typing import Optional, Any
from ...pipeline import Step
from ... import helpers


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


# TODO: migrate to dataclass
class field_update(Step):
    """Update field"""

    code = "field-update"

    def __init__(
        self,
        *,
        name: str,
        value: Optional[Any] = None,
        formula: Optional[Any] = None,
        function: Optional[Any] = None,
        new_name: Optional[str] = None,
        **options,
    ):
        self.name = name
        self.value = value
        self.formula = formula
        self.function = function
        self.new_name = new_name
        self.descriptor = helpers.create_descriptor(**options)

    # Properties

    name: str
    """TODO: add docs"""

    value: Optional[Any]
    """TODO: add docs"""

    formula: Optional[Any]
    """TODO: add docs"""

    function: Optional[Any]
    """TODO: add docs"""

    new_name: Optional[str]
    """TODO: add docs"""

    descriptor: dict
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        function = self.function
        table = resource.to_petl()
        descriptor = self.descriptor.copy()
        if self.new_name:
            descriptor["name"] = self.new_name  # type: ignore
        field = resource.schema.get_field(self.name)
        field.update(descriptor)
        if self.formula:
            function = lambda _, row: simpleeval.simple_eval(self.formula, names=row)
        if function:
            resource.data = table.convert(self.name, function)  # type: ignore
        elif self.new_name:
            resource.data = table.rename({self.name: self.new_name})  # type: ignore
        elif "value" in self.descriptor:
            resource.data = table.update(self.name, self.value)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "newName": {"type": "string"},
        },
    }
