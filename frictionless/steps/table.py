import petl
from ..step import Step
from ..helpers import ResourceView


class merge_tables(Step):
    def __init__(self, *, resource, names=None, ignore_names=False):
        self.__resource = resource
        self.__names = names
        self.__ignore_names = ignore_names

    def transform_resource(self, source, target):
        self.__resource.infer(only_sample=True)
        view1 = ResourceView(source)
        view2 = ResourceView(self.__resource)

        # Ignore names
        if self.__ignore_names:
            target.data = petl.stack(view1, view2)
            for field in self.__resource.schema.fields[len(target.schema.fields) :]:
                target.schema.add_field(field)

        # Default
        else:
            target.data = petl.cat(view1, view2, header=self.__names)
            for field in self.__resource.schema.fields:
                if field.name not in target.schema.field_names:
                    target.schema.add_field(field)
            if self.__names:
                for field in target.schema.fields:
                    if field.name not in self.__names:
                        target.schema.remove_field(field.name)


class join_tables(Step):
    def __init__(self, *, resource, name=None, mode="inner", hash=False):
        assert mode in ["inner", "left", "right", "outer", "cross"]
        self.__resource = resource
        self.__name = name
        self.__mode = mode
        self.__hash = hash

    def transform_resource(self, source, target):
        self.__resource.infer(only_sample=True)
        view1 = ResourceView(source)
        view2 = ResourceView(self.__resource)
        if self.__mode == "inner":
            join = petl.hashjoin if self.__hash else petl.join
            target.data = join(view1, view2, self.__name)
        elif self.__mode == "left":
            leftjoin = petl.hashleftjoin if self.__hash else petl.leftjoin
            target.data = leftjoin(view1, view2, self.__name)
        elif self.__mode == "right":
            rightjoin = petl.hashrightjoin if self.__hash else petl.rightjoin
            target.data = rightjoin(view1, view2, self.__name)
        elif self.__mode == "outer":
            target.data = petl.outerjoin(view1, view2, self.__name)
        elif self.__mode == "cross":
            target.data = petl.crossjoin(view1, view2)
        for field in self.__resource.schema.fields:
            if field.name != self.__name:
                target.schema.fields.append(field.to_copy())


class attach_tables(Step):
    def __init__(self, *, resource):
        self.__resource = resource

    def transform_resource(self, source, target):
        self.__resource.infer(only_sample=True)
        view1 = ResourceView(source)
        view2 = ResourceView(self.__resource)
        target.data = petl.annex(view1, view2)
        for field in self.__resource.schema.fields:
            target.schema.fields.append(field.to_copy())
