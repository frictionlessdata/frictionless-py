import petl
from ..step import Step
from ..field import Field
from ..resource import Resource
from ..exception import FrictionlessException
from .. import helpers


# TODO: implement table_preload/cache step


class table_aggregate(Step):
    code = "table-aggregate"

    def __init__(self, descriptor=None, *, group_name=None, aggregation=None):
        self.setinitial("groupName", group_name)
        self.setinitial("aggregation", aggregation)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__group_name = group_name
        self.__aggregation = aggregation

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().aggregate(self.__group_name, self.__aggregation)
        field = target.schema.get_field(self.__group_name)
        target.schema.fields.clear()
        target.schema.add_field(field)
        for name in self.__aggregation.keys():
            target.schema.add_field(Field(name=name))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "aggregation"],
        "properties": {
            "groupName": {"type": "string"},
            "aggregation": {},
        },
    }


class table_attach(Step):
    code = "table-attach"

    def __init__(self, descriptor=None, *, resource=None):
        self.setinitial("resource", resource)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__resource = resource

    # Transform

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer()
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        target.data = petl.annex(view1, view2)
        for field in self.__resource.schema.fields:
            target.schema.fields.append(field.to_copy())

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
        },
    }


class table_debug(Step):
    code = "table-debug"

    def __init__(self, descriptor=None, *, function=None):
        self.setinitial("function", function)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__function = function

    # Transform

    def transform_resource(self, source, target):

        # Data
        def data():
            for row in source.read_row_stream():
                self.__function(row)
                yield row

        # Meta
        target.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["function"],
        "properties": {
            "function": {},
        },
    }


class table_diff(Step):
    code = "table-diff"

    def __init__(
        self,
        descriptor=None,
        *,
        resource=None,
        ignore_order=False,
        use_hash=False,
    ):
        self.setinitial("resource", resource)
        self.setinitial("ignoreOrder", ignore_order)
        self.setinitial("useHash", use_hash)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__resource = resource
        self.__ignore_order = ignore_order
        self.__use_hash = use_hash

    # Transform

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer()
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        function = petl.recordcomplement if self.__ignore_order else petl.complement
        # TODO: raise an error for ignore/hash
        if self.__use_hash and not self.__ignore_order:
            function = petl.hashcomplement
        target.data = function(view1, view2)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
            "ignoreOrder": {},
            "useHash": {},
        },
    }


class table_intersect(Step):
    code = "table-intersect"

    def __init__(self, descriptor=None, *, resource=None, use_hash=False):
        self.setinitial("resource", resource)
        self.setinitial("useHash", use_hash)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__resource = resource
        self.__use_hash = use_hash

    # Transform

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer()
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        function = petl.hashintersection if self.__use_hash else petl.intersection
        target.data = function(view1, view2)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
            "useHash": {},
        },
    }


class table_join(Step):
    code = "table-join"

    def __init__(
        self,
        descriptor=None,
        *,
        resource=None,
        field_name=None,
        mode="inner",
        hash=False,
    ):
        assert mode in ["inner", "left", "right", "outer", "cross", "anti"]
        self.setinitial("resource", resource)
        self.setinitial("fieldName", field_name)
        self.setinitial("mode", mode)
        self.setinitial("hash", hash)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__resource = resource
        self.__field_name = field_name
        self.__mode = mode
        self.__hash = hash

    # Transform

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer()
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        if self.__mode == "inner":
            join = petl.hashjoin if self.__hash else petl.join
            target.data = join(view1, view2, self.__field_name)
        elif self.__mode == "left":
            leftjoin = petl.hashleftjoin if self.__hash else petl.leftjoin
            target.data = leftjoin(view1, view2, self.__field_name)
        elif self.__mode == "right":
            rightjoin = petl.hashrightjoin if self.__hash else petl.rightjoin
            target.data = rightjoin(view1, view2, self.__field_name)
        elif self.__mode == "outer":
            target.data = petl.outerjoin(view1, view2, self.__field_name)
        elif self.__mode == "cross":
            target.data = petl.crossjoin(view1, view2)
        elif self.__mode == "anti":
            antijoin = petl.hashantijoin if self.__hash else petl.antijoin
            target.data = antijoin(view1, view2, self.__field_name)
        if self.__mode not in ["anti"]:
            for field in self.__resource.schema.fields:
                if field.name != self.__field_name:
                    target.schema.fields.append(field.to_copy())

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
            "fieldName": {"type": "string"},
            "mode": {"type": "string"},
            "hash": {},
        },
    }


class table_melt(Step):
    code = "table-melt"

    def __init__(
        self,
        descriptor=None,
        *,
        field_name=None,
        variables=None,
        to_field_names=["variable", "value"],
    ):
        assert len(to_field_names) == 2
        self.setinitial("fieldName", field_name)
        self.setinitial("variables", variables)
        self.setinitial("toFieldNames", to_field_names)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__field_name = field_name
        self.__variables = variables
        self.__to_field_names = to_field_names

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().melt(
            key=self.__field_name,
            variables=self.__variables,
            variablefield=self.__to_field_names[0],
            valuefield=self.__to_field_names[1],
        )
        field = target.schema.get_field(self.__field_name)
        target.schema.fields.clear()
        target.schema.add_field(field)
        for name in self.__to_field_names:
            target.schema.add_field(Field(name=name))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "variables": {"type": "array"},
            "toFieldNames": {},
        },
    }


class table_merge(Step):
    code = "table-merge"

    def __init__(
        self,
        descriptor=None,
        *,
        resource=None,
        field_names=None,
        ignore_fields=False,
        sort=False,
    ):
        self.setinitial("resource", resource)
        self.setinitial("fieldNames", field_names)
        self.setinitial("ignoreFields", ignore_fields)
        self.setinitial("sort", sort)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__resource = resource
        self.__field_names = field_names
        self.__ignore_fields = ignore_fields
        self.__sort = sort

    # Transform

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer()
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()

        # Ignore fields
        if self.__ignore_fields:
            target.data = petl.stack(view1, view2)
            for field in self.__resource.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)

        # Default
        else:
            if self.__sort:
                target.data = petl.mergesort(
                    view1, view2, key=self.__sort, header=self.__field_names
                )
            else:
                target.data = petl.cat(view1, view2, header=self.__field_names)
            for field in self.__resource.schema.fields:
                if field.name not in target.schema.field_names:
                    target.schema.add_field(field)
            if self.__field_names:
                for field in list(target.schema.fields):
                    if field.name not in self.__field_names:
                        target.schema.remove_field(field.name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
            "fieldNames": {"type": "array"},
            "ignoreFields": {},
            "sort": {},
        },
    }


class table_normalize(Step):
    code = "table-normalize"

    # Transform

    def transform_resource(self, source, target):

        # Data
        # Is it possible here to re-use Row?
        # For example, implementing row.normalize() working in-place
        def data():
            with helpers.ensure_open(source):
                for number, row in enumerate(source.row_stream, start=1):
                    if number == 1:
                        yield row.field_names
                    yield row.to_list()

        target.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


# TODO: improve this step
class table_pivot(Step):
    code = "table-pivot"

    def __init__(self, descriptor=None, **options):
        # TODO: handle options
        super().__init__(descriptor)
        # TODO: reimplement
        self.__options = options

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().pivot(**self.__options)
        # TODO: review this approach
        target.schema.fields.clear()
        target.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_print(Step):
    code = "table-print"

    # Transform

    def transform_resource(self, source, target):
        print(source.to_petl().look(vrepr=str, style="simple"))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_recast(Step):
    code = "table-recast"

    def __init__(
        self,
        descriptor=None,
        *,
        field_name,
        from_field_names=["variable", "value"],
    ):
        assert len(from_field_names) == 2
        self.setinitial("fieldName", field_name)
        self.setinitial("fromFieldName", from_field_names)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__field_name = field_name
        self.__from_field_names = from_field_names

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().recast(
            key=self.__field_name,
            variablefield=self.__from_field_names[0],
            valuefield=self.__from_field_names[1],
        )
        # TODO: review this approach
        target.schema.fields.clear()
        target.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "fromFieldNames": {},
        },
    }


# TODO: fix this step - see tests
class table_transpose(Step):
    code = "table-transpose"

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().transpose()
        # TODO: review this approach
        target.schema.fields.clear()
        target.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


# TODO: improve this step (add an ability to get a report instead of raising?)
class table_validate(Step):
    code = "table-validate"

    # Transform

    def transform_resource(self, source, target):

        # Data
        def data():
            yield source.schema.field_names
            with helpers.ensure_open(source):
                if not source.header.valid:
                    raise FrictionlessException(error=source.header.errors[0])
                for row in source.row_stream:
                    if not row.valid:
                        raise FrictionlessException(error=row.errors[0])
                    yield row

        # Meta
        target.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


# TODO: review this step
class table_write(Step):
    code = "table-write"

    def __init__(self, descriptor=None, *, path=None, **options):
        self.setinitial("path", path)
        # TODO: handle options
        super().__init__(descriptor)
        # TODO: reimplement
        self.__path = path
        self.__options = options

    # Transform

    def transform_resource(self, source, target):
        target.write(Resource(path=self.__path, **self.__options))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
