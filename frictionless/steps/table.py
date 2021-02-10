import petl
from ..step import Step
from ..field import Field
from ..resource import Resource
from ..exception import FrictionlessException


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

    def transform_resource(self, resource):
        group_name = self.get("groupName")
        aggregation = self.get("aggregation")
        field = resource.schema.get_field(group_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in aggregation.keys():
            resource.schema.add_field(Field(name=name))
        yield from resource.to_petl().aggregate(group_name, aggregation)

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

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        source.infer()
        for field in source.schema.fields:
            target.schema.fields.append(field.to_copy())
        view1 = target.to_petl()
        view2 = source.to_petl()
        yield from petl.annex(view1, view2)

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

    def transform_resource(self, resource):
        function = self.get("function")
        with resource:
            for row in resource.row_stream:
                function(row)
                yield row

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

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        ignore_order = self.get("ignoreOrder")
        use_hash = self.get("useHash")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        function = petl.recordcomplement if ignore_order else petl.complement
        # NOTE: we might raise an error for ignore/hash
        if use_hash and not ignore_order:
            function = petl.hashcomplement
        yield from function(view1, view2)

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

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        use_hash = self.get("useHash")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        function = petl.hashintersection if use_hash else petl.intersection
        yield from function(view1, view2)

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

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        field_name = self.get("fieldName")
        use_hash = self.get("useHash")
        mode = self.get("mode")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        if mode not in ["negate"]:
            for field in source.schema.fields:
                if field.name != field_name:
                    target.schema.fields.append(field.to_copy())
        if mode == "inner":
            join = petl.hashjoin if use_hash else petl.join
            yield from join(view1, view2, field_name)
        elif mode == "left":
            leftjoin = petl.hashleftjoin if use_hash else petl.leftjoin
            yield from leftjoin(view1, view2, field_name)
        elif mode == "right":
            rightjoin = petl.hashrightjoin if use_hash else petl.rightjoin
            yield from rightjoin(view1, view2, field_name)
        elif mode == "outer":
            yield from petl.outerjoin(view1, view2, field_name)
        elif mode == "cross":
            yield from petl.crossjoin(view1, view2)
        elif mode == "negate":
            antijoin = petl.hashantijoin if use_hash else petl.antijoin
            yield from antijoin(view1, view2, field_name)

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

    def transform_resource(self, resource):
        variables = self.get("variables")
        field_name = self.get("fieldName")
        to_field_names = self.get("toFieldNames")
        field = resource.schema.get_field(field_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in to_field_names:
            resource.schema.add_field(Field(name=name))
        yield from resource.to_petl().melt(
            key=field_name,
            variables=variables,
            variablefield=to_field_names[0],
            valuefield=to_field_names[1],
        )

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

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        field_names = self.get("fieldNames")
        ignore_fields = self.get("ignoreFields")
        sort_by_field = self.get("sortByField")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()

        # Ignore fields
        if ignore_fields:
            for field in source.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)
            yield from petl.stack(view1, view2)

        # Default
        else:
            for field in source.schema.fields:
                if field.name not in target.schema.field_names:
                    target.schema.add_field(field)
            if field_names:
                for field in list(target.schema.fields):
                    if field.name not in field_names:
                        target.schema.remove_field(field.name)
            if sort_by_field:
                key = sort_by_field
                yield from petl.mergesort(view1, view2, key=key, header=field_names)
            else:
                yield from petl.cat(view1, view2, header=field_names)

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

    def transform_resource(self, resource):
        with resource:
            yield resource.header.to_list()
            for row in resource.row_stream:
                yield row.to_list()

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

    def transform_resource(self, resource):
        options = self.get("options")
        yield from resource.to_petl().pivot(**options)

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

    def transform_resource(self, resource):
        field_name = self.get("fieldName")
        from_field_names = self.get("fromFieldNames")
        yield from resource.to_petl().recast(
            key=field_name,
            variablefield=from_field_names[0],
            valuefield=from_field_names[1],
        )

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

    def transform_resource(self, resource):
        yield resource.to_petl().transpose()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_validate(Step):
    code = "table-validate"

    # Transform

    def transform_resource(self, resource):
        with resource:
            if not resource.header.valid:
                raise FrictionlessException(error=resource.header.errors[0])
            yield resource.header
            for row in resource.row_stream:
                if not row.valid:
                    raise FrictionlessException(error=row.errors[0])
                yield row

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

    def transform_resource(self, resource):
        path = self.get("path")
        options = self.get("options")
        resource.write(Resource(path=path, **options))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
