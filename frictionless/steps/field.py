import simpleeval
from ..step import Step
from ..field import Field
from ..helpers import ResourceView


class pick_fields(Step):
    def __init__(self, *, names):
        self.__names = names

    def transform_resource(self, source, target):
        target.data = ResourceView(source).cut(*self.__names)
        for name in target.schema.field_names:
            if name not in self.__names:
                target.schema.remove_field(name)


class skip_fields(Step):
    def __init__(self, *, names):
        self.__names = names

    def transform_resource(self, source, target):
        target.data = ResourceView(source).cutout(*self.__names)
        for name in self.__names:
            target.schema.remove_field(name)


class move_field(Step):
    def __init__(self, *, name, position):
        self.__name = name
        self.__position = position

    def transform_resource(self, source, target):
        target.data = ResourceView(source).movefield(self.__name, self.__position - 1)
        field = target.schema.remove_field(self.__name)
        target.schema.fields.insert(self.__position - 1, field)


class add_field(Step):
    def __init__(self, *, name, type=None, position=None, value=None):
        self.__name = name
        self.__type = type
        self.__position = position
        self.__value = value

    def transform_resource(self, source, target):
        value = self.__value
        if isinstance(value, str) and value.startswith("<formula>"):
            formula = value.replace("<formula>", "")
            value = lambda row: simpleeval.simple_eval(formula, names=row)
        index = self.__position - 1 if self.__position else None
        target.data = ResourceView(source).addfield(self.__name, value=value, index=index)
        field = Field(name=self.__name, type=self.__type)
        if index is None:
            target.schema.add_field(field)
        else:
            target.schema.fields.insert(index, field)


class add_increment_field(Step):
    def __init__(self, *, name, start=1):
        self.__name = name
        self.__start = start

    def transform_resource(self, source, target):
        target.data = ResourceView(source).addrownumbers(
            field=self.__name, start=self.__start
        )
        field = Field(name=self.__name, type="integer")
        target.schema.fields.insert(0, field)


# TODO: accept WHERE clause
class update_field(Step):
    def __init__(self, *, name, value=None, **options):
        self.__name = name
        self.__value = value
        self.__options = options

    def transform_resource(self, source, target):
        value = self.__value
        if isinstance(value, str) and value.startswith("<formula>"):
            formula = value.replace("<formula>", "")
            value = lambda val, row: simpleeval.simple_eval(formula, names=row)
        elif not callable(value):
            value = lambda val, row: value
        target.data = ResourceView(source).convert(self.__name, value)
        field = target.schema.get_field(self.__name)
        for name, value in self.__options.items():
            setattr(field, name, value)
