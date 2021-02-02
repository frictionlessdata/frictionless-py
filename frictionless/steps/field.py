import petl
import simpleeval
from ..step import Step
from ..field import Field


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_add(Step):
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

    def transform_resource(self, source, target):
        name = self.get("name")
        value = self.get("value")
        formula = self.get("formula")
        function = self.get("function")
        position = self.get("position")
        incremental = self.get("incremental")
        options = self.get("options")
        index = position - 1 if position else None
        if incremental:
            target.data = source.to_petl().addrownumbers(field=name)
        else:
            if formula:
                function = lambda row: simpleeval.simple_eval(formula, names=row)
            value = value or function
            target.data = source.to_petl().addfield(name, value=value, index=index)
        field = Field(name=name, **options)
        if index is None:
            target.schema.add_field(field)
        else:
            target.schema.fields.insert(index, field)

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
    code = "field-filter"

    def __init__(self, descriptor=None, *, names=None):
        self.setinitial("names", names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        names = self.get("names")
        target.data = source.to_petl().cut(*names)
        for name in target.schema.field_names:
            if name not in names:
                target.schema.remove_field(name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }


class field_move(Step):
    code = "field-move"

    def __init__(self, descriptor=None, *, name=None, position=None):
        self.setinitial("name", name)
        self.setinitial("position", position)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        name = self.get("name")
        position = self.get("position")
        target.data = source.to_petl().movefield(name, position - 1)
        field = target.schema.remove_field(name)
        target.schema.fields.insert(position - 1, field)

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
    code = "field-remove"

    def __init__(self, descriptor=None, *, names=None):
        self.setinitial("names", names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        names = self.get("names")
        target.data = source.to_petl().cutout(*names)
        for name in names:
            target.schema.remove_field(name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }


class field_split(Step):
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

    def transform_resource(self, source, target):
        name = self.get("name")
        to_names = self.get("toNames")
        pattern = self.get("pattern")
        preserve = self.get("preserve")
        processor = petl.split
        # NOTE: this condition needs to be improved
        if "(" in pattern:
            processor = petl.capture
        target.data = processor(
            source.to_petl(),
            name,
            pattern,
            to_names,
            include_original=preserve,
        )
        if not preserve:
            target.schema.remove_field(name)
        for name in to_names:
            field = Field(name=name, type="string")
            target.schema.add_field(field)

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
    code = "field-unpack"

    def __init__(self, descriptor=None, *, name, to_names, preserve=False):
        self.setinitial("name", name)
        self.setinitial("toNames", to_names)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        name = self.get("name")
        to_names = self.get("toNames")
        preserve = self.get("preserve")
        if target.schema.get_field(name).type == "object":
            processor = source.to_petl().unpackdict
            target.data = processor(name, to_names, includeoriginal=preserve)
        else:
            processor = source.to_petl().unpack
            target.data = processor(name, to_names, include_original=preserve)
        if not preserve:
            target.schema.remove_field(name)
        for name in to_names:
            field = Field(name=name)
            target.schema.add_field(field)

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

    def transform_resource(self, source, target):
        name = self.get("name")
        value = self.get("value")
        formula = self.get("formula")
        function = self.get("function")
        options = self.get("options")
        if formula:
            function = lambda val, row: simpleeval.simple_eval(formula, names=row)
        if function:
            target.data = source.to_petl().convert(name, function)
        else:
            target.data = source.to_petl().update(name, value)
        field = target.schema.get_field(name)
        for name, value in options.items():
            setattr(field, name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "value": {},
        },
    }
