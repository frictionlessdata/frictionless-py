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
    """Aggregate table"""

    code = "table-aggregate"

    def __init__(self, descriptor=None, *, group_name=None, aggregation=None):
        self.setinitial("groupName", group_name)
        self.setinitial("aggregation", aggregation)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        group_name = self.get("groupName")
        aggregation = self.get("aggregation")
        field = resource.schema.get_field(group_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in aggregation.keys():
            resource.schema.add_field(Field(name=name))
        resource.data = table.aggregate(group_name, aggregation)

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
    """Attach table"""

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
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        for field in source.schema.fields:
            target.schema.fields.append(field.to_copy())
        resource.data = petl.annex(view1, view2)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "resource": {},
        },
    }


class table_debug(Step):
    """Debug table"""

    code = "table-debug"

    def __init__(self, descriptor=None, *, function=None):
        self.setinitial("function", function)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()
        function = self.get("function")

        # Data
        def data():
            with current:
                for row in current.row_stream:
                    function(row)
                    yield row

        # Meta
        resource.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["function"],
        "properties": {
            "function": {},
        },
    }


class table_diff(Step):
    """Diff tables"""

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
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        function = petl.recordcomplement if ignore_order else petl.complement
        # NOTE: we might raise an error for ignore/hash
        if use_hash and not ignore_order:
            function = petl.hashcomplement
        resource.data = function(view1, view2)

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
    """Intersect tables"""

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
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        function = petl.hashintersection if use_hash else petl.intersection
        resource.data = function(view1, view2)

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
    """Join tables"""

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
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()
        if mode not in ["negate"]:
            for field in source.schema.fields:
                if field.name != field_name:
                    target.schema.fields.append(field.to_copy())
        if mode == "inner":
            join = petl.hashjoin if use_hash else petl.join
            resource.data = join(view1, view2, field_name)
        elif mode == "left":
            leftjoin = petl.hashleftjoin if use_hash else petl.leftjoin
            resource.data = leftjoin(view1, view2, field_name)
        elif mode == "right":
            rightjoin = petl.hashrightjoin if use_hash else petl.rightjoin
            resource.data = rightjoin(view1, view2, field_name)
        elif mode == "outer":
            resource.data = petl.outerjoin(view1, view2, field_name)
        elif mode == "cross":
            resource.data = petl.crossjoin(view1, view2)
        elif mode == "negate":
            antijoin = petl.hashantijoin if use_hash else petl.antijoin
            resource.data = antijoin(view1, view2, field_name)

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
    """Melt tables"""

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
        table = resource.to_petl()
        variables = self.get("variables")
        field_name = self.get("fieldName")
        to_field_names = self.get("toFieldNames")
        field = resource.schema.get_field(field_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in to_field_names:
            resource.schema.add_field(Field(name=name))
        resource.data = table.melt(
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
    """Merge tables"""

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
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()
        view1 = target.to_petl()
        view2 = source.to_petl()

        # Ignore fields
        if ignore_fields:
            for field in source.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)
            resource.data = petl.stack(view1, view2)

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
                resource.data = petl.mergesort(view1, view2, key=key, header=field_names)
            else:
                resource.data = petl.cat(view1, view2, header=field_names)

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
    """Normalize table"""

    code = "table-normalize"

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()

        # Data
        def data():
            with current:
                yield current.header.to_list()
                for row in current.row_stream:
                    yield row.to_list()

        # Meta
        resource.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_pivot(Step):
    """Pivot table"""

    code = "table-pivot"

    def __init__(self, descriptor=None, **options):
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        options = self.get("options")
        resource.pop("schema", None)
        resource.data = table.pivot(**options)
        resource.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_print(Step):
    """Print table"""

    code = "table-print"

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        print(table.look(vrepr=str, style="simple"))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_recast(Step):
    """Recast table"""

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
        table = resource.to_petl()
        field_name = self.get("fieldName")
        from_field_names = self.get("fromFieldNames")
        resource.pop("schema", None)
        resource.data = table.recast(
            key=field_name,
            variablefield=from_field_names[0],
            valuefield=from_field_names[1],
        )
        resource.infer()

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
    """Transpose table"""

    code = "table-transpose"

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.pop("schema", None)
        resource.data = table.transpose()
        resource.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_validate(Step):
    """Validate table"""

    code = "table-validate"

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()

        # Data
        def data():
            with current:
                if not current.header.valid:
                    raise FrictionlessException(error=current.header.errors[0])
                yield current.header
                for row in current.row_stream:
                    if not row.valid:
                        raise FrictionlessException(error=row.errors[0])
                    yield row

        # Meta
        resource.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }


class table_write(Step):
    """Write table"""

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
