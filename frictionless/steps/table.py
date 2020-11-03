import petl
from ..step import Step
from ..field import Field
from .. import exceptions


# TODO: implement table_preload/cache step


class table_aggregate(Step):
    def __init__(self, *, group_name, aggregation):
        self.__group_name = group_name
        self.__aggregation = aggregation

    def transform_resource(self, source, target):
        target.data = source.to_petl().aggregate(self.__group_name, self.__aggregation)
        field = target.schema.get_field(self.__group_name)
        target.schema.fields.clear()
        target.schema.add_field(field)
        for name in self.__aggregation.keys():
            target.schema.add_field(Field(name=name))


class table_attach(Step):
    def __init__(self, *, resource):
        self.__resource = resource

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer(only_sample=True)
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        target.data = petl.annex(view1, view2)
        for field in self.__resource.schema.fields:
            target.schema.fields.append(field.to_copy())


class table_debug(Step):
    def __init__(self, *, function):
        self.__function = function

    def transform_resource(self, source, target):

        # Data
        def data():
            yield source.schema.field_names
            for cells in source.read_data_stream():
                self.__function(cells)
                yield cells

        # Meta
        target.data = data


class table_diff(Step):
    def __init__(self, *, resource, ignore_order=False, use_hash=False):
        self.__resource = resource
        self.__ignore_order = ignore_order
        self.__use_hash = use_hash

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer(only_sample=True)
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        function = petl.recordcomplement if self.__ignore_order else petl.complement
        # TODO: raise an error for ignore/hash
        if self.__use_hash and not self.__ignore_order:
            function = petl.hashcomplement
        target.data = function(view1, view2)


class table_intersect(Step):
    def __init__(self, *, resource, use_hash=False):
        self.__resource = resource
        self.__use_hash = use_hash

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer(only_sample=True)
        view1 = source.to_petl()
        view2 = self.__resource.to_petl()
        function = petl.hashintersection if self.__use_hash else petl.intersection
        target.data = function(view1, view2)


class table_join(Step):
    def __init__(self, *, resource, field_name=None, mode="inner", hash=False):
        assert mode in ["inner", "left", "right", "outer", "cross", "anti"]
        self.__resource = resource
        self.__field_name = field_name
        self.__mode = mode
        self.__hash = hash

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer(only_sample=True)
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


class table_melt(Step):
    def __init__(
        self, *, field_name, variables=None, to_field_names=["variable", "value"]
    ):
        assert len(to_field_names) == 2
        self.__field_name = field_name
        self.__variables = variables
        self.__to_field_names = to_field_names

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


class table_merge(Step):
    def __init__(self, *, resource, field_names=None, ignore_fields=False, sort=False):
        self.__resource = resource
        self.__field_names = field_names
        self.__ignore_fields = ignore_fields
        self.__sort = sort

    def transform_resource(self, source, target):
        if isinstance(self.__resource, str):
            self.__resource = source.package.get_resource(self.__resource)
        self.__resource.infer(only_sample=True)
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


class table_normalize(Step):
    def transform_resource(self, source, target):
        target.data = source.read_rows


# TODO: improve this step
class table_pivot(Step):
    def __init__(self, **options):
        self.__options = options

    def transform_resource(self, source, target):
        target.data = source.to_petl().pivot(**self.__options)
        # TODO: review this approach
        target.schema.fields.clear()
        target.infer(only_sample=True)


class table_print(Step):
    def transform_resource(self, source, target):
        print(source.to_petl().look(vrepr=str, style="simple"))


class table_recast(Step):
    def __init__(self, *, field_name, from_field_names=["variable", "value"]):
        assert len(from_field_names) == 2
        self.__field_name = field_name
        self.__from_field_names = from_field_names

    def transform_resource(self, source, target):
        target.data = source.to_petl().recast(
            key=self.__field_name,
            variablefield=self.__from_field_names[0],
            valuefield=self.__from_field_names[1],
        )
        # TODO: review this approach
        target.schema.fields.clear()
        target.infer(only_sample=True)


# TODO: fix this step - see tests
class table_transpose(Step):
    def transform_resource(self, source, target):
        target.data = source.to_petl().transpose()
        # TODO: review this approach
        target.schema.fields.clear()
        target.infer(only_sample=True)


# TODO: improve this step (add an ability to get a report instead of raising?)
class table_validate(Step):
    def transform_resource(self, source, target):

        # Data
        def data():
            yield source.schema.field_names
            with source.to_table() as table:
                if not table.header.valid:
                    raise exceptions.FrictionlessException(error=table.header.errors[0])
                for row in table.row_stream:
                    if not row.valid:
                        raise exceptions.FrictionlessException(error=row.errors[0])
                    yield row

        # Meta
        target.data = data


# TODO: review this step
class table_write(Step):
    def __init__(self, *, path, **options):
        self.__path = path
        self.__options = options

    def transform_resource(self, source, target):
        with target.to_table() as table:
            table.write(self.__path, **self.__options)
