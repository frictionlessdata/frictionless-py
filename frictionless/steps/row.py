import petl
import simpleeval
from ..step import Step


# TODO: review simpleeval perfomance for this transform
# TODO: provide formula/regex helper constructors on the lib level?
class row_filter(Step):
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


class row_search(Step):
    def __init__(self, *, regex, field_name=None, anti=False):
        self.__regex = regex
        self.__field_name = field_name
        self.__anti = anti

    def transform_resource(self, source, target):
        search = petl.searchcomplement if self.__anti else petl.search
        if self.__field_name:
            target.data = search(source.to_petl(), self.__field_name, self.__regex)
        else:
            target.data = search(source.to_petl(), self.__regex)


class row_slice(Step):
    def __init__(self, *, start=None, stop=None, step=None, head=None, tail=None):
        self.__start = start
        self.__stop = stop
        self.__step = step
        self.__head = head
        self.__tail = tail

    def transform_resource(self, source, target):
        if self.__head:
            target.data = source.to_petl().head(self.__head)
        elif self.__tail:
            target.data = source.to_petl().tail(self.__tail)
        else:
            target.data = source.to_petl().rowslice(
                self.__start, self.__stop, self.__step
            )


class row_sort(Step):
    def __init__(self, *, field_names, reverse=False):
        self.__field_names = field_names
        self.__reverse = reverse

    def transform_resource(self, source, target):
        target.data = source.to_petl().sort(self.__field_names, reverse=self.__reverse)


class row_split(Step):
    def __init__(self, *, field_name, pattern):
        self.__field_name = field_name
        self.__pattern = pattern

    def transform_resource(self, source, target):
        target.data = source.to_petl().splitdown(self.__field_name, self.__pattern)


class row_subset(Step):
    def __init__(self, subset, *, field_name=None):
        assert subset in ["conflicts", "distinct", "duplicates", "unique"]
        self.__subset = subset
        self.__field_name = field_name

    def transform_resource(self, source, target):
        if self.__subset == "conflicts":
            target.data = source.to_petl().conflicts(self.__field_name)
        elif self.__subset == "distinct":
            target.data = source.to_petl().distinct(self.__field_name)
        elif self.__subset == "duplicates":
            target.data = source.to_petl().duplicates(self.__field_name)
        elif self.__subset == "unique":
            target.data = source.to_petl().unique(self.__field_name)


class row_ungroup(Step):
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
