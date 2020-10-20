from ..step import Step
from .helpers import ResourceView


class remove_field(Step):
    def __init__(self, field_name):
        self.__field_name = field_name

    def transform_resource(self, source, target):
        target.data = ResourceView(source).cutout(self.__field_name)
        target.schema.remove_field(self.__field_name)
