import simpleeval
from ..step import Step
from ..helpers import ResourceView


class head_rows(Step):
    def __init__(self, *, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = ResourceView(source).head(self.__limit)


class tail_rows(Step):
    def __init__(self, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = ResourceView(source).tail(self.__limit)


class slice_rows(Step):
    def __init__(self, *, start=None, stop, step=None):
        self.__start = start
        self.__stop = stop
        self.__step = step

    def transform_resource(self, source, target):
        target.data = ResourceView(source).rowslice(
            self.__start, self.__stop, self.__step
        )


class filter_rows(Step):
    def __init__(self, *, predicat=None):
        self.__predicat = predicat

    def transform_resource(self, source, target):
        predicat = self.__predicat
        if isinstance(predicat, str) and predicat.startswith("<formula>"):
            formula = predicat.replace("<formula>", "")
            predicat = lambda row: simpleeval.simple_eval(formula, names=row)
        target.data = ResourceView(source).select(predicat)
