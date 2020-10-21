import simpleeval
from ..step import Step
from ..helpers import ResourceView


# TODO: update naming using verb-based?
class head_rows(Step):
    def __init__(self, *, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = ResourceView(source).head(self.__limit)


# TODO: update naming using verb-based?
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


# TODO: review simpleeval perfomance for this transform
# TODO: provide formula/regex helper constructors on the lib level?
class filter_rows(Step):
    def __init__(self, *, predicat=None):
        self.__predicat = predicat

    def transform_resource(self, source, target):
        predicat = self.__predicat
        if isinstance(predicat, str) and predicat.startswith("<formula>"):
            formula = predicat.replace("<formula>", "")
            # TODO: review EvalWithCompoundTypes/sync with checks
            evalclass = simpleeval.EvalWithCompoundTypes
            predicat = lambda row: evalclass(names=row).eval(formula)
        target.data = ResourceView(source).select(predicat)


# TODO: merge with filter_rows?
class search_rows(Step):
    def __init__(self, *, regex, name=None):
        self.__regex = regex
        self.__name = name

    def transform_resource(self, source, target):
        if self.__name:
            target.data = ResourceView(source).search(self.__name, self.__regex)
        else:
            target.data = ResourceView(source).search(self.__regex)


class sort_rows(Step):
    def __init__(self, *, names, reverse=False):
        self.__names = names
        self.__reverse = reverse

    def transform_resource(self, source, target):
        target.data = ResourceView(source).sort(self.__names, reverse=self.__reverse)


# TODO: update naming using verb-based?
class duplicate_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = ResourceView(source).duplicates(self.__name)


# TODO: update naming using verb-based?
class unique_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = ResourceView(source).unique(self.__name)


# TODO: update naming using verb-based?
class conflict_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = ResourceView(source).conflicts(self.__name)
