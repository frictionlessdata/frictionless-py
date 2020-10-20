from ..step import Step
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
