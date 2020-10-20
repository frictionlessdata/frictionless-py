from ..step import Step
from .helpers import ResourceView


class remove_field(Step):
    def __init__(self, *, name):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = ResourceView(source).cutout(self.__name)
        target.schema.remove_field(self.__name)
