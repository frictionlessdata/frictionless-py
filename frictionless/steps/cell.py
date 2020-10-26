import petl
from ..step import Step


# TODO: add set_cells?
# TODO: accept WHERE/PREDICAT clause
class replace_cells(Step):
    def __init__(self, *, pattern, replace, name=None):
        self.__pattern = pattern
        self.__replace = replace
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = source.to_petl().replaceall(self.__pattern, self.__replace)
        else:
            pattern = self.__pattern
            function = petl.replace
            if self.__pattern.startswith("<regex>"):
                pattern = pattern.replace("<regex>", "")
                function = petl.sub
            target.data = function(source.to_petl(), self.__name, pattern, self.__replace)


class fill_cells(Step):
    def __init__(self, *, name=None, value=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.__name = name
        self.__value = value
        self.__direction = direction

    def transform_resource(self, source, target):
        if self.__value:
            target.data = source.to_petl().convert(self.__name, {None: self.__value})
        elif self.__direction == "down":
            if self.__name:
                target.data = source.to_petl().filldown(self.__name)
            else:
                target.data = source.to_petl().filldown()
        elif self.__direction == "right":
            target.data = source.to_petl().fillright()
        elif self.__direction == "left":
            target.data = source.to_petl().fillleft()


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
            target.data = source.to_petl().convertall(value)
        else:
            if not callable(value):
                target.data = source.to_petl().update(self.__name, value)
            else:
                target.data = source.to_petl().convert(self.__name, value)


# TODO: accept WHERE/PREDICAT clause
class format_cells(Step):
    def __init__(self, *, template, name=None):
        self.__template = template
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = source.to_petl().formatall(self.__template)
        else:
            target.data = source.to_petl().format(self.__name, self.__template)


# TODO: accept WHERE/PREDICAT clause
class interpolate_cells(Step):
    def __init__(self, *, template, name=None):
        self.__template = template
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = source.to_petl().interpolateall(self.__template)
        else:
            target.data = source.to_petl().interpolate(self.__name, self.__template)
