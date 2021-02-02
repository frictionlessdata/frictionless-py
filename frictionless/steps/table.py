import petl
from ..step import Step
from ..field import Field
from ..resource import Resource
from ..exception import FrictionlessException
from .. import helpers


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_aggregate(Step):
    code = "table-aggregate"

    def __init__(self, descriptor=None, *, group_name=None, aggregation=None):
        self.setinitial("groupName", group_name)
        self.setinitial("aggregation", aggregation)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        group_name = self.get("groupName")
        aggregation = self.get("aggregation")
        target.data = source.to_petl().aggregate(group_name, aggregation)
        field = target.schema.get_field(group_name)
        target.schema.fields.clear()
        target.schema.add_field(field)
        for name in aggregation.keys():
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

    # Transform

    def transform_resource(self, source, target):
        resource = self.get("resource")
        if isinstance(resource, str):
            resource = source.package.get_resource(resource)
        resource.infer()
        view1 = source.to_petl()
        view2 = resource.to_petl()
        target.data = petl.annex(view1, view2)
        for field in resource.schema.fields:
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

    # Transform

    def transform_resource(self, source, target):
        function = self.get("function")

        # Data
        def data():
            with source:
                for row in source.row_stream:
                    function(row)
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

    # Transform

    def transform_resource(self, source, target):
        resource = self.get("resource")
        ignore_order = self.get("ignoreOrder")
        use_hash = self.get("useHash")
        if isinstance(resource, str):
            resource = source.package.get_resource(resource)
        resource.infer()
        view1 = source.to_petl()
        view2 = resource.to_petl()
        function = petl.recordcomplement if ignore_order else petl.complement
        # NOTE: we might raise an error for ignore/hash
        if use_hash and not ignore_order:
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

    # Transform

    def transform_resource(self, source, target):
        resource = self.get("resource")
        use_hash = self.get("useHash")
        if isinstance(resource, str):
            resource = source.package.get_resource(resource)
        resource.infer()
        view1 = source.to_petl()
        view2 = resource.to_petl()
        function = petl.hashintersection if use_hash else petl.intersection
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
        use_hash=False,
        mode="inner",
    ):
        assert mode in ["inner", "left", "right", "outer", "cross", "negate"]
        self.setinitial("resource", resource)
        self.setinitial("fieldName", field_name)
        self.setinitial("useHash", use_hash)
        self.setinitial("mode", mode)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        resource = self.get("resource")
        field_name = self.get("fieldName")
        use_hash = self.get("useHash")
        mode = self.get("mode")
        if isinstance(resource, str):
            resource = source.package.get_resource(resource)
        resource.infer()
        view1 = source.to_petl()
        view2 = resource.to_petl()
        if mode == "inner":
            join = petl.hashjoin if use_hash else petl.join
            target.data = join(view1, view2, field_name)
        elif mode == "left":
            leftjoin = petl.hashleftjoin if use_hash else petl.leftjoin
            target.data = leftjoin(view1, view2, field_name)
        elif mode == "right":
            rightjoin = petl.hashrightjoin if use_hash else petl.rightjoin
            target.data = rightjoin(view1, view2, field_name)
        elif mode == "outer":
            target.data = petl.outerjoin(view1, view2, field_name)
        elif mode == "cross":
            target.data = petl.crossjoin(view1, view2)
        elif mode == "negate":
            antijoin = petl.hashantijoin if use_hash else petl.antijoin
            target.data = antijoin(view1, view2, field_name)
        if mode not in ["negate"]:
            for field in resource.schema.fields:
                if field.name != field_name:
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
        variables=None,
        field_name=None,
        to_field_names=["variable", "value"],
    ):
        assert len(to_field_names) == 2
        self.setinitial("variables", variables)
        self.setinitial("fieldName", field_name)
        self.setinitial("toFieldNames", to_field_names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        variables = self.get("variables")
        field_name = self.get("fieldName")
        to_field_names = self.get("toFieldNames")
        target.data = source.to_petl().melt(
            key=field_name,
            variables=variables,
            variablefield=to_field_names[0],
            valuefield=to_field_names[1],
        )
        field = target.schema.get_field(field_name)
        target.schema.fields.clear()
        target.schema.add_field(field)
        for name in to_field_names:
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
        sort_by_field=False,
    ):
        self.setinitial("resource", resource)
        self.setinitial("fieldNames", field_names)
        self.setinitial("ignoreFields", ignore_fields)
        self.setinitial("sortByField", sort_by_field)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        resource = self.get("resource")
        field_names = self.get("fieldNames")
        ignore_fields = self.get("ignoreFields")
        sort_by_field = self.get("sortByField")
        if isinstance(resource, str):
            resource = source.package.get_resource(resource)
        resource.infer()
        view1 = source.to_petl()
        view2 = resource.to_petl()

        # Ignore fields
        if ignore_fields:
            target.data = petl.stack(view1, view2)
            for field in resource.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)

        # Default
        else:
            if sort_by_field:
                key = sort_by_field
                target.data = petl.mergesort(view1, view2, key=key, header=field_names)
            else:
                target.data = petl.cat(view1, view2, header=field_names)
            for field in resource.schema.fields:
                if field.name not in target.schema.field_names:
                    target.schema.add_field(field)
            if field_names:
                for field in list(target.schema.fields):
                    if field.name not in field_names:
                        target.schema.remove_field(field.name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
            "fieldNames": {"type": "array"},
            "ignoreFields": {},
            "sortByField": {},
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


class table_pivot(Step):
    code = "table-pivot"

    def __init__(self, descriptor=None, **options):
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        options = self.get("options")
        target.data = source.to_petl().pivot(**options)
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
        self.setinitial("fromFieldNames", from_field_names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        field_name = self.get("fieldName")
        from_field_names = self.get("fromFieldNames")
        target.data = source.to_petl().recast(
            key=field_name,
            variablefield=from_field_names[0],
            valuefield=from_field_names[1],
        )
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


class table_transpose(Step):
    code = "table-transpose"

    # Transform

    def transform_resource(self, source, target):
        target.data = source.to_petl().transpose()
        target.schema.fields.clear()
        target.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


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


class table_write(Step):
    code = "table-write"

    def __init__(self, descriptor=None, *, path=None, **options):
        self.setinitial("path", path)
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        path = self.get("path")
        options = self.get("options")
        target.write(Resource(path=path, **options))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
