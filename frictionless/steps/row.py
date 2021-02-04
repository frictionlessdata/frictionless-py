import petl
import simpleeval
from ..step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_filter(Step):
    code = "row-filter"

    def __init__(self, descriptor=None, *, formula=None, function=None):
        self.setinitial("formula", formula)
        self.setinitial("function", function)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        formula = self.get("formula")
        function = self.get("function")
        if formula:
            # NOTE: review EvalWithCompoundTypes/sync with checks
            evalclass = simpleeval.EvalWithCompoundTypes
            function = lambda row: evalclass(names=row).eval(formula)
        yield from resource.to_petl().select(function)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "formula": {type: "string"},
            "function": {},
        },
    }


class row_search(Step):
    code = "row-search"

    def __init__(self, descriptor=None, *, regex=None, field_name=None, negate=False):
        self.setinitial("regex", regex)
        self.setinitial("fieldName", field_name)
        self.setinitial("negate", negate)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        regex = self.get("regex")
        field_name = self.get("fieldName")
        negate = self.get("negate")
        search = petl.searchcomplement if negate else petl.search
        if field_name:
            yield from search(resource.to_petl(), field_name, regex)
        else:
            yield from search(resource.to_petl(), regex)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["regex"],
        "properties": {
            "regex": {},
            "fieldName": {"type": "string"},
            "negate": {},
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

    # Transform

    def transform_resource(self, resource):
        start = self.get("start")
        stop = self.get("stop")
        step = self.get("step")
        head = self.get("head")
        tail = self.get("tail")
        if head:
            yield from resource.to_petl().head(head)
        elif tail:
            yield from resource.to_petl().tail(tail)
        else:
            yield from resource.to_petl().rowslice(start, stop, step)

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

    # Transform

    def transform_resource(self, resource):
        field_names = self.get("fieldNames")
        reverse = self.get("reverse")
        yield from resource.to_petl().sort(field_names, reverse=reverse)

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

    def __init__(self, descriptor=None, *, pattern=None, field_name=None):
        self.setinitial("pattern", pattern)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        pattern = self.get("pattern")
        field_name = self.get("fieldName")
        yield from resource.to_petl().splitdown(field_name, pattern)

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
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        subset = self.get("subset")
        field_name = self.get("fieldName")
        if subset == "conflicts":
            yield from resource.to_petl().conflicts(field_name)
        elif subset == "distinct":
            yield from resource.to_petl().distinct(field_name)
        elif subset == "duplicates":
            yield from resource.to_petl().duplicates(field_name)
        elif subset == "unique":
            yield from resource.to_petl().unique(field_name)

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
        selection=None,
        group_name=None,
        value_name=None,
    ):
        assert selection in ["first", "last", "min", "max"]
        self.setinitial("selection", selection)
        self.setinitial("groupName", group_name)
        self.setinitial("valueName", value_name)
        super().__init__(descriptor)

    def transform_resource(self, resource):
        selection = self.get("selection")
        group_name = self.get("groupName")
        value_name = self.get("valueName")
        function = getattr(petl, f"groupselect{selection}")
        if selection in ["first", "last"]:
            yield from function(resource.to_petl(), group_name)
        else:
            yield from function(resource.to_petl(), group_name, value_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "selection"],
        "properties": {
            "selection": {"type": "string"},
            "groupName": {"type": "string"},
            "valueName": {"type": "string"},
        },
    }
