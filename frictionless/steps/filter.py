from ..step import Step
from .helpers import ResourceView


class head(Step):
    def __init__(self, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = ResourceView(source).head(self.__limit)


class tail(Step):
    def __init__(self, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = ResourceView(source).tail(self.__limit)
