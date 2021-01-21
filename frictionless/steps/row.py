import petl
import simpleeval
from ..step import Step


# TODO: review simpleeval perfomance for this transform
# TODO: provide formula/regex helper constructors on the lib level?
class row_filter(Step):
    code = "row-filter"

    def __init__(self, descriptor=None, *, predicat=None):
        self.setinitial("predicat", predicat)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__predicat = predicat

    # Transform

    def transform_resource(self, source, target):
        predicat = self.__predicat
        if isinstance(predicat, str) and predicat.startswith("<formula>"):
            formula = predicat.replace("<formula>", "")
            # TODO: review EvalWithCompoundTypes/sync with checks
            evalclass = simpleeval.EvalWithCompoundTypes
            predicat = lambda row: evalclass(names=row).eval(formula)
        target.data = source.to_petl().select(predicat)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["predicat"],
        "properties": {
            "predicat": {},
        },
    }


class row_search(Step):
    code = "row-search"

    def __init__(self, descriptor=None, *, regex=None, field_name=None, anti=False):
        self.setinitial("regex", regex)
        self.setinitial("fieldName", field_name)
        self.setinitial("anti", anti)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__regex = regex
        self.__field_name = field_name
        self.__anti = anti

    # Transform

    def transform_resource(self, source, target):
        search = petl.searchcomplement if self.__anti else petl.search
        if self.__field_name:
            target.data = search(source.to_petl(), self.__field_name, self.__regex)
        else:
            target.data = search(source.to_petl(), self.__regex)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["regex"],
        "properties": {
            "regex": {},
            "fieldName": {"type": "string"},
            "anti": {},
        },
    }


class row_slice(Step):
    code = "row-slice"

    def __init__(
        self,
        descriptor=None,
        *,
        start=None,
        stop=None,
        step=None,
        head=None,
        tail=None,
    ):
        self.setinitial("start", start)
        self.setinitial("stop", stop)
        self.setinitial("step", step)
        self.setinitial("head", head)
        self.setinitial("tail", tail)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__start = start
        self.__stop = stop
        self.__step = step
        self.__head = head
        self.__tail = tail

    # Transform

    def transform_resource(self, source, target):
        if self.__head:
            target.data = source.to_petl().head(self.__head)
        elif self.__tail:
            target.data = source.to_petl().tail(self.__tail)
        else:
            target.data = source.to_petl().rowslice(
                self.__start, self.__stop, self.__step
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "start": {},
            "stop": {},
            "step": {},
            "head": {},
            "tail": {},
        },
    }


class row_sort(Step):
    code = "row-sort"

    def __init__(self, descriptor=None, *, field_names=None, reverse=False):
        self.setinitial("fieldNames", field_names)
        self.setinitial("reverse", reverse)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__field_names = field_names
        self.__reverse = reverse

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().sort(self.__field_names, reverse=self.__reverse)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldNames"],
        "properties": {
            "fieldNames": {"type": "array"},
            "reverse": {},
        },
    }


class row_split(Step):
    code = "row-add"

    def __init__(self, descriptor=None, *, field_name=None, pattern=None):
        self.setinitial("fieldName", field_name)
        self.setinitial("pattern", pattern)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__field_name = field_name
        self.__pattern = pattern

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().splitdown(self.__field_name, self.__pattern)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName", "pattern"],
        "properties": {
            "fieldName": {"type": "string"},
            "pattern": {"type": "string"},
        },
    }


class row_subset(Step):
    code = "row-subset"

    def __init__(self, descriptor=None, *, subset=None, field_name=None):
        assert subset in ["conflicts", "distinct", "duplicates", "unique"]
        self.setinitial("subset", subset)
        self.setinitial("fieldNames", field_name)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__subset = subset
        self.__field_name = field_name

    # Transform

    def transform_resource(self, source, target):
        if self.__subset == "conflicts":
            target.data = source.to_petl().conflicts(self.__field_name)
        elif self.__subset == "distinct":
            target.data = source.to_petl().distinct(self.__field_name)
        elif self.__subset == "duplicates":
            target.data = source.to_petl().duplicates(self.__field_name)
        elif self.__subset == "unique":
            target.data = source.to_petl().unique(self.__field_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["subset"],
        "properties": {
            "subset": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }


class row_ungroup(Step):
    code = "row-ungroup"

    def __init__(
        self,
        descriptor=None,
        *,
        group_name=None,
        selection=None,
        value_name=None,
    ):
        assert selection in ["first", "last", "min", "max"]
        self.setinitial("groupName", group_name)
        self.setinitial("selection", selection)
        self.setinitial("valueName", value_name)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__group_name = group_name
        self.__selection = selection
        self.__value_name = value_name

    def transform_resource(self, source, target):
        function = getattr(petl, f"groupselect{self.__selection}")
        if self.__selection in ["first", "last"]:
            target.data = function(source.to_petl(), self.__group_name)
        else:
            target.data = function(source.to_petl(), self.__group_name, self.__value_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "selection"],
        "properties": {
            "groupName": {"type": "string"},
            "selection": {"type": "string"},
            "valueName": {"type": "string"},
        },
    }
