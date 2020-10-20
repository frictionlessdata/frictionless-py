import petl
from ..step import Step
from ..helpers import ResourceView


class merge_table(Step):
    def __init__(self, *, resource, names=None):
        self.__resource = resource
        self.__names = names

    def transform_resource(self, source, target):
        self.__resource.infer(only_sample=True)
        view1 = ResourceView(source)
        view2 = ResourceView(self.__resource)
        target.data = petl.cat(view1, view2, header=self.__names)
        for field in self.__resource.schema.fields:
            if field.name not in target.schema.field_names:
                target.schema.add_field(field)
        if self.__names:
            for field in target.schema.fields:
                if field.name not in self.__names:
                    target.schema.remove_field(field.name)
