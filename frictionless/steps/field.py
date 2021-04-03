import petl
import simpleeval
from ..step import Step
from ..field import Field


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
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        value = self.get("value")
        formula = self.get("formula")
        function = self.get("function")
        position = self.get("position")
        incremental = self.get("incremental")
        options = self.get("options")
        field = Field(name=name, **options)
        index = position - 1 if position else None
        if index is None:
            resource.schema.add_field(field)
        else:
            resource.schema.fields.insert(index, field)
        if incremental:
            resource.data = table.addrownumbers(field=name)
        else:
            if formula:
                function = lambda row: simpleeval.simple_eval(formula, names=row)
            value = value or function
            resource.data = table.addfield(name, value=value, index=index)

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


class field_filter(Step):
    """Filter fields"""

    code = "field-filter"

    def __init__(self, descriptor=None, *, names=None):
        self.setinitial("names", names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        names = self.get("names")
        for name in resource.schema.field_names:
            if name not in names:
                resource.schema.remove_field(name)
        resource.data = table.cut(*names)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }


class field_move(Step):
    """Move field"""

    code = "field-move"

    def __init__(self, descriptor=None, *, name=None, position=None):
        self.setinitial("name", name)
        self.setinitial("position", position)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        position = self.get("position")
        field = resource.schema.remove_field(name)
        resource.schema.fields.insert(position - 1, field)
        resource.data = table.movefield(name, position - 1)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "position"],
        "properties": {
            "name": {"type": "string"},
            "position": {"type": "number"},
        },
    }


class field_remove(Step):
    """Remove field"""

    code = "field-remove"

    def __init__(self, descriptor=None, *, names=None):
        self.setinitial("names", names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        names = self.get("names")
        for name in names:
            resource.schema.remove_field(name)
        resource.data = table.cutout(*names)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }


class field_split(Step):
    """Split field"""

    code = "field-split"

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        to_names=None,
        pattern=None,
        preserve=False,
    ):
        self.setinitial("name", name)
        self.setinitial("toNames", to_names)
        self.setinitial("pattern", pattern)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        to_names = self.get("toNames")
        pattern = self.get("pattern")
        preserve = self.get("preserve")
        for to_name in to_names:
            resource.schema.add_field(Field(name=to_name, type="string"))
        if not preserve:
            resource.schema.remove_field(name)
        processor = petl.split
        # NOTE: this condition needs to be improved
        if "(" in pattern:
            processor = petl.capture
        resource.data = processor(
            table,
            name,
            pattern,
            to_names,
            include_original=preserve,
        )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "toNames", "pattern"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {},
            "pattern": {},
            "preserve": {},
        },
    }


class field_unpack(Step):
    """Unpack field"""

    code = "field-unpack"

    def __init__(self, descriptor=None, *, name, to_names, preserve=False):
        self.setinitial("name", name)
        self.setinitial("toNames", to_names)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        to_names = self.get("toNames")
        preserve = self.get("preserve")
        field = resource.schema.get_field(name)
        for to_name in to_names:
            resource.schema.add_field(Field(name=to_name))
        if not preserve:
            resource.schema.remove_field(name)
        if field.type == "object":
            processor = table.unpackdict
            resource.data = processor(name, to_names, includeoriginal=preserve)
        else:
            processor = table.unpack
            resource.data = processor(name, to_names, include_original=preserve)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "toNames"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {"type": "array"},
            "preserve": {},
        },
    }


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
        **options,
    ):
        self.setinitial("name", name)
        self.setinitial("value", value)
        self.setinitial("formula", formula)
        self.setinitial("function", function)
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        value = self.get("value")
        formula = self.get("formula")
        function = self.get("function")
        options = self.get("options")
        field = resource.schema.get_field(name)
        for item in options.items():
            setattr(field, item[0], item[1])
        if formula:
            function = lambda val, row: simpleeval.simple_eval(formula, names=row)
        if function:
            resource.data = table.convert(name, function)
        elif "value" in self:
            resource.data = table.update(name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "value": {},
        },
    }
