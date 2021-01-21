import petl
import simpleeval
from ..step import Step
from ..field import Field


class field_add(Step):
    code = "field-add"

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        value=None,
        position=None,
        incremental=False,
        **options,
    ):
        self.setinitial("name", name)
        self.setinitial("value", value)
        self.setinitial("position", position)
        self.setinitial("incremental", incremental)
        # TODO: add options
        super().__init__(descriptor)
        # TODO: reimplement
        self.__name = name
        self.__value = value
        self.__position = position if not incremental else 1
        self.__incremental = incremental
        self.__options = options

    # Transform

    def transform_resource(self, source, target):
        index = self.__position - 1 if self.__position else None
        if self.__incremental:
            target.data = source.to_petl().addrownumbers(field=self.__name)
        else:
            value = self.__value
            if isinstance(value, str) and value.startswith("<formula>"):
                formula = value.replace("<formula>", "")
                value = lambda row: simpleeval.simple_eval(formula, names=row)
            target.data = source.to_petl().addfield(self.__name, value=value, index=index)
        field = Field(name=self.__name, **self.__options)
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
        # TODO: reimplement
        self.__names = names

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().cut(*self.__names)
        for name in target.schema.field_names:
            if name not in self.__names:
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
        # TODO: reimplement
        self.__name = name
        self.__position = position

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().movefield(self.__name, self.__position - 1)
        field = target.schema.remove_field(self.__name)
        target.schema.fields.insert(self.__position - 1, field)

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
        # TODO: reimplement
        self.__names = names

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().cutout(*self.__names)
        for name in self.__names:
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
        # TODO: reimplement
        self.__name = name
        self.__to_names = to_names
        self.__pattern = pattern
        self.__preserve = preserve

    # Transform

    def transform_resource(self, source, target):
        processor = petl.split
        # TODO: implement this check properly
        if "(" in self.__pattern:
            processor = petl.capture
        target.data = processor(
            source.to_petl(),
            self.__name,
            self.__pattern,
            self.__to_names,
            include_original=self.__preserve,
        )
        if not self.__preserve:
            target.schema.remove_field(self.__name)
        for name in self.__to_names:
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
        # TODO: reimplement
        self.__name = name
        self.__to_names = to_names
        self.__preserve = preserve

    # Transform

    def transform_resource(self, source, target):
        if target.schema.get_field(self.__name).type == "object":
            target.data = source.to_petl().unpackdict(
                self.__name, self.__to_names, includeoriginal=self.__preserve
            )
        else:
            target.data = source.to_petl().unpack(
                self.__name, self.__to_names, include_original=self.__preserve
            )
        if not self.__preserve:
            target.schema.remove_field(self.__name)
        for name in self.__to_names:
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


# TODO: accept WHERE/PREDICAT clause
class field_update(Step):
    code = "field-update"

    def __init__(self, descriptor=None, *, name=None, value=None, **options):
        self.setinitial("name", name)
        self.setinitial("value", value)
        # TODO: handle options
        super().__init__(descriptor)
        # TODO: reimplement
        self.__name = name
        self.__value = value
        self.__options = options

    # Transform

    def transform_resource(self, source, target):
        value = self.__value
        if isinstance(value, str) and value.startswith("<formula>"):
            formula = value.replace("<formula>", "")
            value = lambda val, row: simpleeval.simple_eval(formula, names=row)
        if not callable(value):
            target.data = source.to_petl().update(self.__name, value)
        else:
            target.data = source.to_petl().convert(self.__name, value)
        field = target.schema.get_field(self.__name)
        for name, value in self.__options.items():
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
