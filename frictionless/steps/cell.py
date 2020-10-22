import petl
from ..step import Step
from ..helpers import ResourceView


# TODO: add set_cells?
# TODO: accept WHERE/PREDICAT clause
class replace_cells(Step):
    def __init__(self, *, pattern, replace, name=None):
        self.__pattern = pattern
        self.__replace = replace
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = ResourceView(source).replaceall(self.__pattern, self.__replace)
        else:
            pattern = self.__pattern
            function = petl.replace
            if self.__pattern.startswith("<regex>"):
                pattern = pattern.replace("<regex>", "")
                function = petl.sub
            target.data = function(
                ResourceView(source), self.__name, pattern, self.__replace
            )


class fill_cells(Step):
    def __init__(self, *, name=None, value=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.__name = name
        self.__value = value
        self.__direction = direction

    def transform_resource(self, source, target):
        if self.__value:
            target.data = ResourceView(source).convert(self.__name, {None: self.__value})
        elif self.__direction == "down":
            if self.__name:
                target.data = ResourceView(source).filldown(self.__name)
            else:
                target.data = ResourceView(source).filldown()
        elif self.__direction == "right":
            target.data = ResourceView(source).fillright()
        elif self.__direction == "left":
            target.data = ResourceView(source).fillleft()


# TODO: accept WHERE/PREDICAT clause
class convert_cells(Step):
    def __init__(self, *, value, name=None):
        self.__value = value
        self.__name = name

    def transform_resource(self, source, target):
        value = self.__value
        if not self.__name:
            if not callable(value):
                value = lambda val: self.__value
            target.data = ResourceView(source).convertall(value)
        else:
            if not callable(value):
                target.data = ResourceView(source).update(self.__name, value)
            else:
                target.data = ResourceView(source).convert(self.__name, value)


# TODO: accept WHERE/PREDICAT clause
class format_cells(Step):
    def __init__(self, *, template, name=None):
        self.__template = template
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = ResourceView(source).formatall(self.__template)
        else:
            target.data = ResourceView(source).format(self.__name, self.__template)


# TODO: accept WHERE/PREDICAT clause
class interpolate_cells(Step):
    def __init__(self, *, template, name=None):
        self.__template = template
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = ResourceView(source).interpolateall(self.__template)
        else:
            target.data = ResourceView(source).interpolate(self.__name, self.__template)
