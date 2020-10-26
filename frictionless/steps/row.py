import petl
import simpleeval
from ..step import Step


# TODO: update naming using verb-based?
class head_rows(Step):
    def __init__(self, *, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = source.to_petl().head(self.__limit)


# TODO: update naming using verb-based?
class tail_rows(Step):
    def __init__(self, limit):
        self.__limit = limit

    def transform_resource(self, source, target):
        target.data = source.to_petl().tail(self.__limit)


class slice_rows(Step):
    def __init__(self, *, start=None, stop, step=None):
        self.__start = start
        self.__stop = stop
        self.__step = step

    def transform_resource(self, source, target):
        target.data = source.to_petl().rowslice(self.__start, self.__stop, self.__step)


# TODO: add skip_rows
# TODO: rename to pick_rows
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
        target.data = source.to_petl().select(predicat)


# TODO: merge with filter_rows?
class search_rows(Step):
    def __init__(self, *, regex, name=None, anti=False):
        self.__regex = regex
        self.__name = name
        self.__anti = anti

    def transform_resource(self, source, target):
        search = petl.searchcomplement if self.__anti else petl.search
        if self.__name:
            target.data = search(source.to_petl(), self.__name, self.__regex)
        else:
            target.data = search(source.to_petl(), self.__regex)


class sort_rows(Step):
    def __init__(self, *, names, reverse=False):
        self.__names = names
        self.__reverse = reverse

    def transform_resource(self, source, target):
        target.data = source.to_petl().sort(self.__names, reverse=self.__reverse)


# TODO: update naming using verb-based?
class duplicate_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = source.to_petl().duplicates(self.__name)


# TODO: update naming using verb-based?
class unique_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = source.to_petl().unique(self.__name)


# TODO: update naming using verb-based?
class conflict_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = source.to_petl().conflicts(self.__name)


# TODO: update naming using verb-based?
class distinct_rows(Step):
    def __init__(self, *, name=None):
        self.__name = name

    def transform_resource(self, source, target):
        target.data = source.to_petl().distinct(self.__name)


class split_rows(Step):
    def __init__(self, *, name, pattern):
        self.__name = name
        self.__pattern = pattern

    def transform_resource(self, source, target):
        target.data = source.to_petl().splitdown(self.__name, self.__pattern)


class pick_group_rows(Step):
    def __init__(self, *, group_name, selection, value_name=None):
        assert selection in ["first", "last", "min", "max"]
        self.__group_name = group_name
        self.__selection = selection
        self.__value_name = value_name

    def transform_resource(self, source, target):
        function = getattr(petl, f"groupselect{self.__selection}")
        if self.__selection in ["first", "last"]:
            target.data = function(source.to_petl(), self.__group_name)
        else:
            target.data = function(source.to_petl(), self.__group_name, self.__value_name)
