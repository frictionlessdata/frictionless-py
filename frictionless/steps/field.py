from ..step import Step
from .helper import ResourceView


class remove_field(Step):
    def __init__(self, field_name):
        self.__field_name = field_name

    def transform_resource(self, source, target):
        target.schema.remove_field(self.__field_name)
        yield from ResourceView(source).cutout(self.__field_name)
